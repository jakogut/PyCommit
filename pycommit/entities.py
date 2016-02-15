class CRMEntity(object):
    types = {
        "Account": 10,
        "Accounts": 10,
        "Opportunitity": 20,
        "Opportunities": 20,
        "Document": 30,
        "Documents": 30,
        "Charge": 40,
        "Charges": 40,
        "Event": 50,
        "Events": 50,
        "HistoryNote": 60,
        "HistoryNotes": 60,
        "Ticket": 70,
        "Tickets": 70,
        "Item": 80,
        "Items": 80,
        "Asset": 90,
        "Assets": 90,
        "KBArticle": 100,
        "KBArticles": 100
    }

    def __init__(self, crm_proxy=None, recid=None, auto_populate=True):
        self.db_data = {}

        if recid: self.set_recid(recid)
        self.entity_type = None

        if self.get_recid() is not None \
        and crm_proxy is not None \
        and auto_populate is True:
            self.populate(crm_proxy)

        self._sub_values()

    # Commit will return values that are different from what it accepts.
    def _sub_values(self):
        try:
            for key, value in self.db_data.items():
                if value in self.value_map:
                    self.db_data[key] = self.value_map[value]
        except AttributeError:
            return

    def set_recid(self, recid):
        self.db_data[self._recid_field] = recid

    def get_recid(self):
        if self._recid_field in self.db_data:
            return self.db_data[self._recid_field]
        else: return None

    def get_field(self, field):
        if field not in self.db_fields: return ''
        mapped = self.db_fields[field]

        if mapped not in self.db_data: return ''
        return self.db_data[mapped]

    def set_field(self, field, value):
        mapped = self.db_fields[field]
        self.db_data[mapped] = value

    def create(self, crm_proxy):
        if self.get_recid() is not None:
            return

        self._db_sync(crm_proxy)

    def update(self, crm_proxy):
        if self.get_recid() is None:
            return

        self._db_sync(crm_proxy)

    def _db_sync(self, crm_proxy):
        crm_proxy.update_record_from_dict(self.entity_type, self.db_data)

    def populate_field(self, crm_proxy, field_name):
        value = crm_proxy.get_field(self.get_recid(), field_name)
        if value: self.db_data[field_name] = value
        self._sub_values()

    def populate(self, crm_proxy):
        field_names = []
        for _, field_name in self.db_fields.items():
            self.populate_field(crm_proxy, field_name)

class Account(CRMEntity):
    db_fields = {
        "AccountRecID": "FLDCRDRECID",
        "AccountMgr": "FLDCRDASSIGNCARDID",
        "SubContStatus": "FLDCRDSUBCONTSTATUS",
        "CompanyName": "FLDCRDCOMPANY",
        "Contact": "FLDCRDCONTACT",
        "Username": "FLDWRKUSERNAME",
        "Assistant": "FLDCRDASSISTANT",
        "Contract": "FLDCRDBCRECID",
        "AccountNumber": "FLDCRDCARDID2",
        "ID": "FLDCRDCARDID3",
        "PopupMessage": "FLDCRDCARDMESSAGE",
        "AddressLn1": "FLDCRDADDRESS1",
        "AddressLn2": "FLDCRDADDRESS2",
        "AddressLn3": "FLDCRDADDRESS3",
        "AddressCity": "FLDCRDCITY",
        "AddressState": "FLDCRDSTATE",
        "AddressCountry": "FLDCRDCOUNTRY",
        "AddressZip": "FLDCRDZIP",
        "CreationDate": "FLDCRDCREATEDATE",
        "CreatedByUser": "FLDCRDCREATEUSERID",
        "Dear": "FLDCRDDEAR",
        "Department": "FLDCRDDEPARTMENT",
        "DocStorDir": "FLDCRDDOCSFOLDER",
        "Email1": "FLDCRDEMAIL1",
        "Email2": "FLDCRDEMAIL1",
        "AccountType": "FLDCRDENTITYKIND",
        "FaxNumber": "FLDCRDFAX1",
        "FaxExt": "FLDCRDFAXDESC1",
        "FileAs": "FLDCRDFULLNAME",
        "Type": "FLDCRDKIND",
        "LastName": "FLDCRDLASTNAME",
        "Notes": "FLDCRDNOTES",
        "Field": "FLDCRDPERSONID",
        "Phone1": "FLDCRDPHONE1",
        "Phone2": "FLDCRDPHONE2",
        "Phone3": "FLDCRDPHONE3",
        "Phone4": "FLDCRDPHONE4",
        "PhoneExt1": "FLDCRDPHNDESC1",
        "PhoneExt2": "FLDCRDPHNDESC2",
        "PhoneExt3": "FLDCRDPHNDESC3",
        "PhoneExt4": "FLDCRDPHNDESC4",
        "Region": "FLDCRDREGIONCODE",
        "PopMessIndc": "FLDCRDSHOWMESSAGE",
        "SubContactCode": "FLDCRDSUBCODE",
        "Salutation": "FLDCRDSUFFIX",
        "Tax1": "FLDCRDTAXCODE1",
        "Tax2": "FLDCRDTAXCODE2",
        "Title": "FLDCRDTITLE",
        "LastUpdtBy": "FLDCRDUPDATEUSERID",
        "WebAddr1": "FLDCRDURL1",
        "WebAddr2": "FLDCRDURL2",
        "Status": "FLDCRDUSER1",
        "Field1": "FLDCRDUSER2",
        "Field2": "FLDCRDUSER3",
        "Field3": "FLDCRDUSER4",
        "Field4": "FLDCRDUSER5"
    }

    def __init__(self, crm_proxy=None, recid=None, auto_populate=True):
        self._recid_field = self.db_fields['AccountRecID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['Account']

class Asset(CRMEntity):
    db_fields = {
        "Code": "FLDASTASSETCODE",
        "Type": "FLDASTASSETTYPE",  # Required
        "Name": "FLDASTNAME",
        "Status": "FLDASTSTATUS",   # Required
        "RecordID": "FLDASTRECID",
        "SerialNo": "FLDASTSERIALNO",
        "AccountRecID": "FLDASTACCRECID",
        "Contact": "FLDASTCONTACTRECID",
        "CreatedByUser": "FLDASTCREATEUSER",
        "PurchaseDate": "FLDASTCUSTPURDATE",
        "PurchasedFromUs": "FLDASTCUSTPURFROMUS",
        "PurchaseInvoiceNo": "FLDASTCUSTPUROURINV",
        "CustomerPO": "FLDASTCUSTPURPO",
        "PurchasePrice": "FLDASTCUSTPURPRICE",
        "DeliveredDate": "FLDASTDELIVEDATE",
        "Description": "FLDASTDESC",
        "InstalledBy": "FLDASTINSTALBY",
        "InstalledDate": "FLDASTINSTALDATE",
        "LicenseCodes": "FLDASTLICENSECODE",
        "LicenseKeys": "FLDASTLICENSEKEYS",
        "LicenseNotes": "FLDASTLICENSENOTES",
        "Location": "FLDASTLOCATION",
        "Manufacturer": "FLDASTMANUFACTURER",
        "MnfSerialNo": "FLDASTMNFSERIALNO",
        "Model": "FLDASTMODEL",
        "Notes": "FLDASTNOTES",
        "Quantity": "FLDASTQUANTITY",
        "LastUpdateBy": "FLDASTUPDATEUSER",
        "Field1": "FLDASTUSER1",
        "Field2": "FLDASTUSER2",
        "Field3": "FLDASTUSER3",
        "Field4": "FLDASTUSER4",
        "Field5": "FLDASTUSER5",
        "Date1": "FLDASTUSERDATE1",
        "Number1": "FLDASTUSERNUMBER1",
        "VendorPurchDate": "FLDASTVENDORDATEPURC",
        "VendorInvoiceNo": "FLDASTVENDORINVNO",
        "VendorPO": "FLDASTVENDOROURPO",
        "VendorPrice": "FLDASTVENDORPRICE",
        "Vendor": "FLDASTVENDORRECID",
        "VendorSerialNo": "FLDASTVENDORSERNO",
        "VendorWarrExp": "FLDASTVENDORWARREXP",
        "Version": "FLDASTVERSION",
        "WarrExpDate": "FLDASTWARREXPDATE"
    }

    def __init__(self, crm_proxy=None, recid=None, auto_populate=True):
        self._recid_field = self.db_fields['RecordID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['Asset']

class Charge(CRMEntity):
    db_fields = {
        "RecordID": "FLDSLPRECID",
        "ChargeSource": "FLDSLPSOURCERECID",
        "AccountRecID": "FLDSLPCARDID",
        "EmployeeRecID": "FLDSLPWORKERID",
        "ChargedItem": "FLDSLPITEMID",
        "ContractRecID": "FLDSLPBCRECID",
        "TicketRecID": "FLDSLPTICKETID",
        "Date": "FLDSLPSLIPDATE",
        "Description": "FLDSLPDESC",
        "Units": "FLDSLPQUANTITY",
        "HoursAmount": "FLDSLPHOURSAMOUNT",
        "AdjustAmount": "FLDSLPADJUSTAMOUNT",
        "AdjustPercent": "FLDSLPADJUSTPERCENT",
        "FromTime": "FLDSLPSTARTTIME",
        "ToTime": "FLDSLPENDTIME",
        "Price": "FLDSLPPRICE",
        "Billable": "FLDSLPBILLKIND",
        "Billed": "FLDSLPSTAGE",
        "Field1": "FLDSLPUSER1",
        "CreateUser": "FLDSLPCREATEUSER"
    }

    value_map = {
        'Billable': 'B',
        'Not Billable': 'N',
        'Draft' : 'D',
        'Billed': 'B',
    }

    def __init__(self, crm_proxy=None, recid=None, auto_populate=True):
        self._recid_field = self.db_fields['RecordID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['Charge']

class HistoryNote(CRMEntity):
    db_fields = {
        "RecordID": "FLDHISRECID",
        "Date": "FLDHISNOTEDATETIME",
        "Description": "FLDHISDESCRIPTION",
        "LinkRecID": "FLDHISLINKRECID",
        "Field": "FLDHISUSER1",
        "About": "FLDHISKIND",
        "Employee": "FLDHISWORKERID",
        "Account": "FLDHISCARDID",
        "Contact": "FLDHISCONTACTID",
        "Document": "FLDHISDOCID",
        "CreatedByUser": "FLDHISCREATEUSER"
    }

    def __init__(self, crm_proxy=None, recid=None, auto_populate=True):
        self._recid_field = self.db_fields['RecordID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['HistoryNote']

class Item(CRMEntity):
    db_fields = {
        "RecordID": "FLDITMRECID",
        "ItemGroup": "FLDITMITEMTYPEGROUP",
        "ItemCode": "FLDITMITEMNO",
        "ItemName": "FLDITMNAME",
        "PriceSource": "FLDITMPRICESOURCE",
        "PricePerUnit": "FLDITMUNITISHOUR",
        "Price": "FLDITMUNITPRICE",
        "Cost": "FLDITMSTANDARDCOST",
        "Taxes1": "FLDITMTAXCODE1",
        "Taxes2": "FLDITMTAXCODE2",
        "Taxes3": "FLDITMTAXCODE3",
        "DescByName": "FLDITMDESCBYNAME",
        "Description": "FLDITMDESC",
        "Suspend": "FLDITMSUSPENDED",
        "Notes": "FLDITMNOTES",
        "Field1": "FLDITMUSER1",
        "CreateUser": "FLDITMCREATEUSER",
        "CreatedByUSer": "FLDITMCREATEUSER"
    }

    value_map = {
        'Product/Part': 'P',
        'per unit': 'N',
        'Fixed Price': 'F',
    }

    def __init__(self, crm_proxy=None, recid=None, code=None, suspended=False, auto_populate=True):
        if code and crm_proxy and not recid:
            code_recid = self._code_to_recid(crm_proxy, code, suspended)
            if code_recid: recid = code_recid

        self._recid_field = self.db_fields['RecordID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['Item']
        self._sub_values()

    def _code_to_recid(self, crm_proxy, code, suspended):
        suspend_flag = 'Y' if suspended == True else 'N'

        recid = crm_proxy.get_recids('ITEM',
                {ItemFields['ItemCode']: code, ItemFields['Suspend']: suspend_flag})

        if not recid: return

        if len(recid) > 1:
            raise GeneralError

        return recid[0]

class Ticket(CRMEntity):
    db_fields = {
        "AccountRecID": "FLDTKTCARDID",
        "ContactRecID": "FLDTKTCONTACTID",
        "ContractRecID": "FLDTKTBCRECID",
        "AssetRecID": "FLDTKTASSETRECID",
        "EmpRecID": "FLDTKTWORKERID",
        "Priority": "FLDTKTPRIORITY",
        "TicketNumber": "FLDTKTTICKETNO",
        "TicketRecID":  "FLDTKTRECID",
        "Description": "FLDTKTPROBLEM",
        "TicketType": "FLDTKTKIND",
        "Source": "FLDTKTSOURCE",
        "EstDuration": "FLDTKTSCHEDLENESTIM",
        "ShowTktInDisp": "FLDTKTFORDISPATCH",
        "Status": "FLDTKTSTATUS",
        "CreatedByUser": "FLDTKTCREATEUSER",
        "DueDate": "FLDTKTDUEDATETIME",
        "Resolution": "FLDTKTSOLUTION"
    }

    def __init__(self, crm_proxy=None, recid=None, tktno=None, auto_populate=True):
        if tktno and crm_proxy and not recid:
            ticket_recid = self._tktno_to_recid(crm_proxy, tktno)
            if ticket_recid: recid = ticket_recid
            
        self._recid_field = self.db_fields['TicketRecID']
        super().__init__(crm_proxy, recid, auto_populate)
        self.entity_type = self.types['Ticket']

    def _tktno_to_recid(self, crm_proxy, tktno):
        recid = crm_proxy.get_recids('TICKET', {TicketFields['TicketNumber']: tktno})

        if len(recid) > 1: raise GeneralError
        return recid[0]

# legacy compatibility
Entity = CRMEntity.types
AccountFields = Account.db_fields
AssetFields = Asset.db_fields
ChargeFields = Charge.db_fields
HistoryNoteFields = HistoryNote.db_fields
ItemFields = Item.db_fields
TicketFields = Ticket.db_fields

if __name__ == '__main__':
    from xmlrpc.client import ServerProxy
    crm_proxy = ServerProxy('http://10.10.200.67:8000', allow_none=True)
    acct = Account(crm_proxy, 'CRDO4H7A4S453D55P4JJ')

    print(acct.db_data)
