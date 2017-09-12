# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_lots
)
from openprocurement.tender.belowthreshold.tests.lot import (
    TenderLotResourceTestMixin,
    TenderLotFeatureResourceTestMixin,
    TenderLotProcessTestMixin
)
from openprocurement.tender.belowthreshold.tests.lot_blanks import (
    # TenderLotResourceTest
    tender_lot_guarantee,
)

from openprocurement.tender.openua.tests.base import (
    test_bids, BaseTenderUAContentWebTest, test_tender_data,
    test_features_tender_ua_data
)
from openprocurement.tender.openua.tests.lot_blanks import (
    # TenderLotResourceTest
    patch_tender_currency,
    patch_tender_vat,
    get_tender_lot,
    get_tender_lots,
    # TenderLotEdgeCasesTest
    question_blocking,
    claim_blocking,
    next_check_value_with_unanswered_question,
    next_check_value_with_unanswered_claim,
    # TenderLotBidderResourceTest
    create_tender_bidder_invalid,
    patch_tender_bidder,
    # TenderLotFeatureBidderResourceTest
    create_tender_bidder_feature_invalid,
    create_tender_bidder_feature,
    # TenderLotProcessTest
    proc_1lot_1bid,
    proc_1lot_1bid_patch,
    proc_1lot_2bid,
    proc_1lot_3bid_1un,
    proc_2lot_1bid_0com_1can,
    proc_2lot_2bid_1lot_del,
    proc_2lot_1bid_2com_1win,
    proc_2lot_1bid_0com_0win,
    proc_2lot_1bid_1com_1win,
    proc_2lot_2bid_2com_2win,
    lots_features_delete,
    proc_2lot_2bid_1claim_1com_1win,
)


class TenderUALotResourceTestMixin(object):
    test_patch_tender_currency = snitch(patch_tender_currency)
    test_patch_tender_vat = snitch(patch_tender_vat)
    test_get_tender_lot = snitch(get_tender_lot)
    test_get_tender_lots = snitch(get_tender_lots)


class TenderUALotProcessTestMixin(object):
    test_proc_1lot_1bid_patch = snitch(proc_1lot_1bid_patch)
    test_proc_1lot_2bid = snitch(proc_1lot_2bid)
    test_proc_1lot_3bid_1un = snitch(proc_1lot_3bid_1un)
    test_proc_2lot_2bid_2com_2win = snitch(proc_2lot_2bid_2com_2win)


class TenderLotResourceTest(BaseTenderUAContentWebTest, TenderLotResourceTestMixin, TenderUALotResourceTestMixin):
    initial_data = test_tender_data
    test_lots_data = test_lots

    test_tender_lot_guarantee = snitch(tender_lot_guarantee)


class TenderLotEdgeCasesTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots * 2
    initial_bids = test_bids

    test_question_blocking = snitch(question_blocking)
    test_claim_blocking = snitch(claim_blocking)
    test_next_check_value_with_unanswered_question = snitch(next_check_value_with_unanswered_question)
    test_next_check_value_with_unanswered_claim = snitch(next_check_value_with_unanswered_claim)


class TenderLotFeatureResourceTest(BaseTenderUAContentWebTest, TenderLotFeatureResourceTestMixin):
    initial_data = test_tender_data
    initial_lots = 2 * test_lots
    invalid_feature_value = 0.5
    max_feature_value = 0.3
    sum_of_max_value_of_all_features = 0.3

class TenderLotBidderResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_patch_tender_bidder = snitch(patch_tender_bidder)


class TenderLotFeatureBidderResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots

    def setUp(self):
        super(TenderLotFeatureBidderResourceTest, self).setUp()
        self.lot_id = self.initial_lots[0]['id']
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(self.tender_id, self.tender_token), {"data": {
            "items": [
                {
                    'relatedLot': self.lot_id,
                    'id': '1'
                }
            ],
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": "1",
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": self.lot_id,
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]
        }})
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['data']['items'][0]['relatedLot'], self.lot_id)

    test_create_tender_bidder_feature_invalid = snitch(create_tender_bidder_feature_invalid)
    test_create_tender_bidder_feature = snitch(create_tender_bidder_feature)


class TenderLotProcessTest(BaseTenderUAContentWebTest, TenderLotProcessTestMixin, TenderUALotProcessTestMixin):
    initial_data = test_tender_data
    test_lots_data = test_lots
    test_features_tender_data = test_features_tender_ua_data
    setUp = BaseTenderUAContentWebTest.setUp

    days_till_auction_starts = 16

    test_proc_1lot_1bid = snitch(proc_1lot_1bid)
    test_proc_2lot_1bid_0com_1can = snitch(proc_2lot_1bid_0com_1can)
    test_proc_2lot_2bid_1lot_del = snitch(proc_2lot_2bid_1lot_del)
    test_proc_2lot_1bid_2com_1win = snitch(proc_2lot_1bid_2com_1win)
    test_proc_2lot_1bid_0com_0win = snitch(proc_2lot_1bid_0com_0win)
    test_proc_2lot_1bid_1com_1win = snitch(proc_2lot_1bid_1com_1win)
    test_lots_features_delete = snitch(lots_features_delete)
    test_proc_2lot_2bid_1claim_1com_1win = snitch(proc_2lot_2bid_1claim_1com_1win)

    def test_lots_features_delete(self):
        # create tender
        response = self.app.post_json('/tenders', {'data': test_features_tender_ua_data})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        tender = response.json['data']
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        self.assertEqual(tender['features'], test_features_tender_ua_data['features'])
        # add lot
        lots = []
        for lot in test_lots * 2:
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': lot})
            self.assertEqual(response.status, '201 Created')
            self.assertEqual(response.content_type, 'application/json')
            lots.append(response.json['data']['id'])

        # add features
        response = self.app.patch_json('/tenders/{}?acc_token={}&opt_pretty=1'.format(tender['id'], owner_token), {'data': {
            "features": [
                {
                    "code": "code_item",
                    "featureOf": "item",
                    "relatedItem": '1',
                    "title": u"item feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_lot",
                    "featureOf": "lot",
                    "relatedItem": lots[1],
                    "title": u"lot feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                },
                {
                    "code": "code_tenderer",
                    "featureOf": "tenderer",
                    "title": u"tenderer feature",
                    "enum": [
                        {
                            "value": 0.01,
                            "title": u"good"
                        },
                        {
                            "value": 0.02,
                            "title": u"best"
                        }
                    ]
                }
            ]}})
        # create bid
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lots[1]}],
                                                'parameters': [
                                                               {"code": "code_lot","value": 0.01},
                                                               {"code": "code_tenderer","value": 0.01}],
                                                'tenderers': [test_organization]}})
        self.assertEqual(response.status, '201 Created')
        self.assertEqual(response.content_type, 'application/json')
        bid_id = response.json['data']['id']
        bid_token = response.json['access']['token']
        # delete features
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], owner_token), {'data': {'features': []}})
        response = self.app.get('/tenders/{}?opt_pretty=1'.format(tender_id))
        self.assertNotIn('features', response.json['data'])
        # patch bid without parameters
        response = self.app.patch_json('/tenders/{}/bids/{}?acc_token={}'.format(tender_id, bid_id, bid_token),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                                'status': "active",
                                                'lotValues': [{"value": {"amount": 500}, 'relatedLot': lots[1]}],
                                                'parameters': [],
                                                'tenderers': [test_organization]}})
        self.assertEqual(response.status, '200 OK')
        self.assertNotIn('parameters', response.json['data'])

    def test_2lot_2bid_1claim_1com_1win(self):
        # create tender
        response = self.app.post_json('/tenders', {"data": test_tender_data})
        tender_id = self.tender_id = response.json['data']['id']
        owner_token = response.json['access']['token']
        lots = []
        for lot in 2 * test_lots:
            # add lot
            response = self.app.post_json('/tenders/{}/lots?acc_token={}'.format(tender_id, owner_token), {'data': test_lots[0]})
            self.assertEqual(response.status, '201 Created')
            lots.append(response.json['data']['id'])
        self.initial_lots = lots
        # add item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": [test_tender_data['items'][0] for i in lots]}})
        # add relatedLot for item
        response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender_id, owner_token), {"data": {"items": [{'relatedLot': i} for i in lots]}})
        self.assertEqual(response.status, '200 OK')
        # switch to active.tendering
        response = self.set_status('active.tendering', {"lots": [
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
            for i in lots
        ]})
        # create bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                                      'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': lot_id}
            for lot_id in lots
        ]}})
        bid_token = response.json['access']['token']
        # create second bid
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.post_json('/tenders/{}/bids'.format(tender_id), {'data': {'selfEligible': True, 'selfQualified': True,
                                                                                      'tenderers': [test_organization], 'lotValues': [
            {"value": {"amount": 500}, 'relatedLot': lot_id}
            for lot_id in lots
        ]}})
        # switch to active.auction
        self.set_status('active.auction')
        # get auction info
        self.app.authorization = ('Basic', ('auction', ''))
        response = self.app.get('/tenders/{}/auction'.format(tender_id))
        auction_bids_data = response.json['data']['bids']
        for lot_id in lots:
            # posting auction urls
            response = self.app.patch_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {
                'data': {
                    'lots': [
                        {
                            'id': i['id'],
                            'auctionUrl': 'https://tender.auction.url'
                        }
                        for i in response.json['data']['lots']
                    ],
                    'bids': [
                        {
                            'id': i['id'],
                            'lotValues': [
                                {
                                    'relatedLot': j['relatedLot'],
                                    'participationUrl': 'https://tender.auction.url/for_bid/{}'.format(i['id'])
                                }
                                for j in i['lotValues']
                            ],
                        }
                        for i in auction_bids_data
                    ]
                }
            })
            # posting auction results
            self.app.authorization = ('Basic', ('auction', ''))
            response = self.app.post_json('/tenders/{}/auction/{}'.format(tender_id, lot_id), {'data': {'bids': auction_bids_data}})
        # for first lot
        lot_id = lots[0]
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        # add complaint
        response = self.app.post_json('/tenders/{}/awards/{}/complaints?acc_token={}'.format(tender_id, award_id, bid_token),
                                      {'data': {'title': 'complaint title',
                                                'description': 'complaint description',
                                                'author': test_organization,
                                                'relatedLot': lot_id,
                                                'status': 'claim'}})
        self.assertEqual(response.status, '201 Created')
        # cancel lot
        response = self.app.post_json('/tenders/{}/cancellations?acc_token={}'.format(tender_id, owner_token),
                                      {'data': {'reason': 'cancellation reason',
                                       'status': 'active',
                                       "cancellationOf": "lot",
                                       "relatedLot": lot_id}})
        self.assertEqual(response.status, '201 Created')
        # for second lot
        lot_id = lots[1]
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as unsuccessful
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "unsuccessful"}})
        # get awards
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}/awards?acc_token={}'.format(tender_id, owner_token))
        # get pending award
        award_id = [i['id'] for i in response.json['data'] if i['status'] == 'pending' and i['lotID'] == lot_id][0]
        # set award as active
        self.app.patch_json('/tenders/{}/awards/{}?acc_token={}'.format(tender_id, award_id, owner_token), {"data": {"status": "active", "qualified": True, "eligible": True}})
        # get contract id
        response = self.app.get('/tenders/{}'.format(tender_id))
        contract_id = response.json['data']['contracts'][-1]['id']
        # after stand slill period
        self.set_status('complete', {'status': 'active.awarded'})
        # time travel
        tender = self.db.get(tender_id)
        for i in tender.get('awards', []):
            i['complaintPeriod']['endDate'] = i['complaintPeriod']['startDate']
        self.db.save(tender)
        # sign contract
        self.app.authorization = ('Basic', ('broker', ''))
        self.app.patch_json('/tenders/{}/contracts/{}?acc_token={}'.format(tender_id, contract_id, owner_token), {"data": {"status": "active"}})
        # check status
        self.app.authorization = ('Basic', ('broker', ''))
        response = self.app.get('/tenders/{}'.format(tender_id))
        self.assertTrue([i['status'] for i in response.json['data']['lots']], ['cancelled', 'complete'])
        self.assertEqual(response.json['data']['status'], 'complete')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderLotResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotFeatureBidderResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotProcessTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
