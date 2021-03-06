# Build a simple blockchain

[![Build Status](https://www.travis-ci.org/VincentGau/hakuCoin.svg?branch=master)](https://www.travis-ci.org/VincentGau/hakuCoin)

## Simple Example
### Run server on different ports
```
python main.py
python main.py -p 5001
python main.py -p 5002
```

[Postman](https://www.getpostman.com) is suggested to send requests and view responses.

Now we can:  
- `http://{node}/full_chain` to view all blocks.  eg. `http://localhost:5000/full_chain`
- `http://{node}/mine` to store all pending transaction in a new block add the block to the blockchain, which is the so-called mining.
- `http://{node}/resolve` to apply the consensus algorithm, determine which chain should be authoritative, in this case, the longest chain is used.
- `http://{node}/wallet` to apply for a new wallet. Including key pair and address.
- Post data to `http://{node}/transact` to claim a new transaction, the transaction should be broadcasted to all nodes in the network.
- Post data to `http://{node}/transact_safe` to claim a new transaction in the safe mode (with transaction digest and signature), the transaction should be broadcasted to all nodes in the network.
- Post data to `http://{node}register_nodes` to join the network, the request should be sent to all _other_ nodes in the network.


### Register nodes to the network
Nodes info are configured in `local_config.py` by default. We can also add nodes to the network manually.
eg. If the nodes set() is empty, post json below to `http://localhost:5000/register_nodes`.
```
{
	"nodes": ["http://localhost:5001", "http://localhost:5002"]
}

```
then node 5000 will notice 5001 and 5002. Do the same request to 5001 and 5002 to let them know each other, now the three of them make a preliminary p2p network.

### Add new transaction 
Broadcast requests to all nodes in the network. eg. post json below to `http://localhost:5000/transact`.
```
{
	"sender": "haku", 
	"recipient": "chihiro",
	"amount": 3
}
```
and to servers on port 5001, 5002 as well.

### A safe way to claim transactions from client
run `python wallet.py` to see the testcase

### Mining
Let's suppose node 5000 mine the block first, `http://localhost:5000/mine`. After that, when we vist `http://localhost:5000/full_chain`, we'll see a new block was added to the chain, transaction was stored in that block. 

### Resolve conflick
Meanwhile, blockchains in node 5001 and 5002 still got only one block - the genesis block. To resolve the conflict, we choose the longest chain. `http://localhost:5001/resolve` and we'll update the blockchain in node 5001.


### generate local wallet files
uncomment `# generate_keys_file()` and run `wallet.py` to generate a local key file.