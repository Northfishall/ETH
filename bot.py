
from web3 import Web3
from web3.auto import w3
import time 
from binascii import hexlify
import sendemail


v2_contract_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
local_http = "http://localhost:8545"

def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt

def connect_http(url):
    #连接本地节点
    web3 = Web3(Web3.HTTPProvider(url))
    if web3.isConnected:
        return web3
    else:
        raise RuntimeError('以太坊HTTP连接错误')
        return web3


def get_event(web3):
    ################################
    #过滤event V2
    v2_filter = web3.eth.filter({"address":v2_contract_address,fromBlock:20000, toBlock:'latest'})
    print("Filter result :")
    print(v2_filter)
    #################################

def contract_connect(web3):
    v2_uniswap = web3.contract.Contract(v2_contract_address)
    print(v2_uniswap)
    print(type(v2_uniswap))
    v2_info = web3.eth.contract.ConciseContract(v2_uniswap)
    print(type(v2_info))
    print(v2_info)

def get_transaction_info(web3):
    #获取当前区块交易哈希列表
    transactions_info = []
    transactions_receipt = []
    block = web3.eth.getBlock('latest')
    transactions_hash_list = block['transactions']
    #############仅供实验时候用 显示时间
    timestamp = block['timestamp']
    print(timestamp_datetime(int(timestamp)))
    #############
    #根据当前区块的交易哈希值来获取交易的详细信息
    for transaction in transactions_hash_list:
        # transactions_info.append(web3.eth.getTransaction(transaction))
        encode_transactiong = "0x"+ str(hexlify(transaction).decode("utf-8"))
        print(encode_transactiong)
        try:
            transactions_info.append( web3.eth.getTransaction(encode_transactiong))
        except Exception as e :
            transactions_info.append("Null")
            continue
        try:
            transactions_receipt.append(web3.eth.getTransactionReceipt(encode_transactiong))
        except Exception as e :
            transactions_receipt.append("Null")
    return transactions_info, transactions_receipt

def get_code(web3):
    code = web3.eth.getCode(Web3.toChecksumAddress('0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852'))
    print(code)
    # print(code.encode('utf-8'))
    print(hexlify(code).decode("utf-8"))

def process_transaction_info(web,transactions_info,transactions_receipt):
    print(transactions_info[0]['from'])
    print(transactions_info[0]['to'])
    print(transactions_info[0]['value'])
    #input -- 与交易一起发送的数据
    input_data = transactions_info[0]['input']
    print(input_data)
    function_code = input_data[0:10]
    to_code = input_data[10:47]
    value_code = input_data[47:]
    print(function_code)
    print(to_code)
    print(value_code)
    #contractAddress --部署的合约的地址
    print(transactions_receipt[0]['contractAddress'])

    #获取当前区块的unxi时间戳 将其转化为北京时间
    print("timestamp:")
    timestamp = web3.eth.getBlock('latest')['timestamp']
    date = timestamp_datetime(int(timestamp))
    print(date)
    # new_block_filter = w3.eth.filter('latest')
    # print(new_block_filter.get_new_entries())

#通过监视v2 factory contract发出的交易来确认是否有新的合约发出 并且通过交易收据来确认新的合约的地址

def monitory_v2():
    web3 = connect_http(local_http)
    new_contract_address = []
    while 1:
        transactions_info, transactions_receipt = get_transaction_info(web3)
        for info , receipt  in zip(transactions_info , transactions_receipt):
            print(info['from'])
            if str(info['from']) == v2_contract_address:
                new_contract = receipt['contractAddress']
                new_contract_address.append(new_contract)
                subject = "new contarct from v2 factory contract."
                print(subject)
                msg = new_contract
                sendemail.sendemail(subject,msg)
                print("send email")
        time.sleep(1)








if __name__=='__main__':
    monitory_v2()

