# transfer 
transfer脚本分单线程和多线程。

脚本的转账功能是通过cli_wallet提供的接口，进行签名转账的。所以，运行脚本要求：

* 有运行的cli_wallet，并且通过-r参数提供websocket接口。即脚本中的url。

* cli_wallet需要unlock状态。

* cli_wallet需要import_key转账from账号私钥。

