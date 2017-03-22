from openprocurement.api.utils import (
    upload_file, context_unpack, json_view,
    update_file_content_type, get_now
)
from openprocurement.tender.core.utils import (
    save_tender,
    apply_patch,
    optendersresource,
    calculate_business_date
)
from openprocurement.api.validation import ViewPermissionValidationError
from openprocurement.tender.core.validation import (
    validate_operation_with_tender_document_in_not_allowed_status,
    validate_tender_period_extension_in_active_tendering
)
from openprocurement.api.validation import validate_file_upload, validate_file_update, validate_patch_document_data
from openprocurement.tender.belowthreshold.views.tender_document import TenderDocumentResource
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD


@optendersresource(name='aboveThresholdUA:Tender Documents',
                   collection_path='/tenders/{tender_id}/documents',
                   path='/tenders/{tender_id}/documents/{document_id}',
                   procurementMethodType='aboveThresholdUA',
                   description="Tender UA related binary files (PDFs, etc.)")
class TenderUaDocumentResource(TenderDocumentResource):

    def validate_update_tender(self, operation):
        try:
            validate_operation_with_tender_document_in_not_allowed_status(self.request, operation)
            validate_tender_period_extension_in_active_tendering(self.request, TENDERING_EXTRA_PERIOD)
        except ViewPermissionValidationError:
            return
        else:
            return True

    @json_view(permission='upload_tender_documents', validators=(validate_file_upload,))
    def collection_post(self):
        """Tender Document Upload"""
        if not self.validate_update_tender('add'):
            return
        document = upload_file(self.request)
        self.context.documents.append(document)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.context.invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info('Created tender document {}'.format(document.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_create'}, {'document_id': document.id}))
            self.request.response.status = 201
            document_route = self.request.matched_route.name.replace("collection_", "")
            self.request.response.headers['Location'] = self.request.current_route_url(_route_name=document_route, document_id=document.id, _query={})
            return {'data': document.serialize("view")}

    @json_view(permission='upload_tender_documents', validators=(validate_file_update,))
    def put(self):
        """Tender Document Update"""
        if not self.validate_update_tender('update'):
            return
        document = upload_file(self.request)
        self.request.validated['tender'].documents.append(document)
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if save_tender(self.request):
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_put'}))
            return {'data': document.serialize("view")}

    @json_view(content_type="application/json", permission='upload_tender_documents', validators=(validate_patch_document_data,))
    def patch(self):
        """Tender Document Update"""
        if not self.validate_update_tender('update'):
            return
        if self.request.authenticated_role == 'tender_owner' and self.request.validated['tender_status'] == 'active.tendering':
            self.request.validated['tender'].invalidate_bids_data()
        if apply_patch(self.request, src=self.request.context.serialize()):
            update_file_content_type(self.request)
            self.LOGGER.info('Updated tender document {}'.format(self.request.context.id),
                        extra=context_unpack(self.request, {'MESSAGE_ID': 'tender_document_patch'}))
            return {'data': self.request.context.serialize("view")}
