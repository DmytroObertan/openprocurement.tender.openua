# -*- coding: utf-8 -*-
from openprocurement.api.models import get_now
from openprocurement.api.views.contract import TenderAwardContractResource
from openprocurement.api.utils import (
    apply_patch,
    check_tender_status,
    context_unpack,
    json_view,
    opresource,
    save_tender,
    check_merged_contracts,
)
from openprocurement.api.validation import validate_patch_contract_data


@opresource(name='Tender UA Contracts',
            collection_path='/tenders/{tender_id}/contracts',
            path='/tenders/{tender_id}/contracts/{contract_id}',
            procurementMethodType='aboveThresholdUA',
            description="Tender contracts")
class TenderUaAwardContractResource(TenderAwardContractResource):

    @staticmethod
    def award_valid(request, awardID, additional=False):
        tender = request.validated['tender']
        award = [a for a in tender.awards if a.id == awardID][0]
        stand_still_end = award.complaintPeriod.endDate
        if stand_still_end > get_now():
            error_message = 'Can\'t sign contract before stand-still{additional} period end ({end_date})'.format(
                additional=" additional awards" if additional else "",
                end_date=stand_still_end.isoformat())
            request.errors.add('body', 'data', error_message)
            request.errors.status = 403
            return False
        pending_complaints = [
            i
            for i in tender.complaints
            if i.status in tender.block_complaint_status and i.relatedLot in [None, award.lotID]
            ]
        pending_awards_complaints = [
            i
            for a in tender.awards
            for i in a.complaints
            if i.status in tender.block_complaint_status and a.lotID == award.lotID
            ]
        if pending_complaints or pending_awards_complaints:
            error_message = 'Can\'t sign contract before reviewing all{additional} complaints'.format(
                additional=" additional" if additional else "")
            request.errors.add('body', 'data', error_message)
            request.errors.status = 403
            return False
        return True

    @json_view(content_type="application/json", permission='edit_tender', validators=(validate_patch_contract_data,))
    def patch(self):
        """Update of contract
        """
        if self.request.validated['tender_status'] not in ['active.qualification', 'active.awarded']:
            self.request.errors.add('body', 'data', 'Can\'t update contract in current ({}) tender status'.format(self.request.validated['tender_status']))
            self.request.errors.status = 403
            return
        tender = self.request.validated['tender']
        if any([i.status != 'active' for i in tender.lots if i.id in [a.lotID for a in tender.awards if a.id == self.request.context.awardID]]):
            self.request.errors.add('body', 'data', 'Can update contract only in active lot status')
            self.request.errors.status = 403
            return
        if any([any([c.status == 'accepted' for c in i.complaints]) for i in tender.awards if i.lotID in [a.lotID for a in tender.awards if a.id == self.request.context.awardID]]):
            self.request.errors.add('body', 'data', 'Can\'t update contract with accepted complaint')
            self.request.errors.status = 403
            return
        data = self.request.validated['data']
        contract = self.request.validated['contract']

        if data['value']:
            for ro_attr in ('valueAddedTaxIncluded', 'currency'):
                if data['value'][ro_attr] != getattr(self.context.value, ro_attr):
                    self.request.errors.add('body', 'data', 'Can\'t update {} for contract value'.format(ro_attr))
                    self.request.errors.status = 403
                    return

            award = [a for a in tender.awards if a.id == self.request.context.awardID][0]
            max_sum = award.value.amount
            # If contract has additionalAwardIDs then add value.amount to mac contract value
            if 'additionalAwardIDs' in contract and contract['additionalAwardIDs']:
                max_sum += sum([award.value.amount for award in tender.awards
                                if award['id'] in contract['additionalAwardIDs']])
            if data['value']['amount'] > max_sum:
                self.request.errors.add('body', 'data',
                                        'Value amount should be less or equal to awarded amount ({})'.format(max_sum))
                self.request.errors.status = 403
                return

        if self.request.context.status != 'active' and 'status' in data and data['status'] == 'active':
            if not self.award_valid(self.request, self.request.context.awardID):  # check main contract
                return
            for awardID in contract.get('additionalAwardIDs'):
                if not self.award_valid(self.request, awardID, additional=True):  # if get errors then return them
                    return
        if check_merged_contracts(self.request) is not None:
            return
        contract_status = self.request.context.status
        apply_patch(self.request, save=False, src=self.request.context.serialize())
        if contract_status != self.request.context.status and (contract_status != 'pending' or self.request.context.status != 'active'):
            self.request.errors.add('body', 'data', 'Can\'t update contract status')
            self.request.errors.status = 403
            return
        if self.request.context.status == 'active' and not self.request.context.dateSigned:
            self.request.context.dateSigned = get_now()
        check_tender_status(self.request)
        if save_tender(self.request):
            self.LOGGER.info('Updated tender contract {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_contract_patch'}))
            return {'data': self.request.context.serialize()}
