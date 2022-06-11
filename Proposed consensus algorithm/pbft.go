package main

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"sync"
	"time"
)
const base_format = "2006-01-02 15:04:05.000000000"
//本地消息池（模拟持久化层），只有确认提交成功后才会存入此池
var localMessagePool = []Message{}
var starttamp int64
//var end time.Time
// timeall time.Duration
type node struct {
	//节点ID
	nodeID string
	//节点监听地址
	addr string
	//RSA私钥
	rsaPrivKey []byte
	//RSA公钥
	rsaPubKey []byte
}

type pbft struct {
	//节点信息
	node node
	//每笔请求自增序号
	sequenceID int
	//锁
	lock sync.Mutex
	//临时消息池，消息摘要对应消息本体
	messagePool map[string]Request
	//存放收到的prepare数量(至少需要收到并确认2f个)，根据摘要来对应
	prePareConfirmCount map[string]map[string]bool
	//存放收到的commit数量（至少需要收到并确认2f+1个），根据摘要来对应
	commitConfirmCount map[string]map[string]bool
	//该笔消息是否已进行Commit广播
	isCommitBordcast map[string]bool
	//该笔消息是否已对客户端进行Reply
	isReply map[string]bool
}

func NewPBFT(nodeID, addr string) *pbft {
	p := new(pbft)
	p.node.nodeID = nodeID
	p.node.addr = addr
	p.node.rsaPrivKey = p.getPivKey(nodeID) //从生成的私钥文件处读取
	p.node.rsaPubKey = p.getPubKey(nodeID)  //从生成的私钥文件处读取
	p.sequenceID = 0
	p.messagePool = make(map[string]Request)
	p.prePareConfirmCount = make(map[string]map[string]bool)
	p.commitConfirmCount = make(map[string]map[string]bool)
	p.isCommitBordcast = make(map[string]bool)
	p.isReply = make(map[string]bool)
	return p
}

func (p *pbft) handleRequest(data []byte) {
	//切割消息，根据消息命令调用不同的功能
	cmd, content := splitMessage(data)
	switch command(cmd) {
	case cRequest:
		p.handleClientRequest(content)
	case cPrePrepare:
		p.handlePrePrepare(content)
	case cReply:
		p.handleReply(content)
	}
}

//处理客户端发来的请求
func (p *pbft) handleClientRequest(content []byte) {
	fmt.Println("主节点已接收到客户端发来的request ...")
	//使用json解析出Request结构体
	r := new(Request)
	err := json.Unmarshal(content, r)
	starttamp = r.Timestamp
	if err != nil {
		log.Panic(err)
	}
	//添加信息序号
	p.sequenceIDAdd()
	//获取消息摘要
	digest := getDigest(*r)
	fmt.Println("digest", digest)
	fmt.Println("已将request存入临时消息池")
	//存入临时消息池
	p.messagePool[digest] = *r
	//主节点对消息摘要进行签名
	digestByte, _ := hex.DecodeString(digest)
	signInfo := p.RsaSignWithSha256(digestByte, p.node.rsaPrivKey)
	//拼接成PrePrepare，准备发往follower节点
	pp := PrePrepare{*r, digest, p.sequenceID, signInfo}
	b, err := json.Marshal(pp)
	if err != nil {
		log.Panic(err)
	}
	fmt.Println("正在向其他节点进行进行消息广播 ...")
	//进行PrePrepare广播
	p.broadcast(cPrePrepare, b)
	fmt.Println("消息广播完成")
}

//处理主节点发送的消息
func (p *pbft) handlePrePrepare(content []byte) {
	fmt.Println("本节点已接收到主节点发来的消息 ...")
	//	//使用json解析出PrePrepare结构体
	pp := new(PrePrepare)
	err := json.Unmarshal(content, pp)
	if err != nil {
		log.Panic(err)
	}
	//获取主节点的公钥，用于数字签名验证
	primaryNodePubKey := p.getPubKey("N0")
	digestByte, _ := hex.DecodeString(pp.Digest)
	if digest := getDigest(pp.RequestMessage); digest != pp.Digest {
		fmt.Println("信息摘要对不上，拒绝进行回复")
	} else if p.sequenceID+1 != pp.SequenceID {
		fmt.Println("消息序号对不上，拒绝进行回复")
	} else if !p.RsaVerySignWithSha256(digestByte, pp.Sign, primaryNodePubKey) {
		fmt.Println("主节点签名验证失败！,拒绝进行回复")
	} else {
		//序号赋值
		p.sequenceID = pp.SequenceID
		//将信息存入临时消息池
		fmt.Println("已将消息存入临时节点池")
		p.messagePool[pp.Digest] = pp.RequestMessage
		//节点使用私钥对其签名
		sign := p.RsaSignWithSha256(digestByte, p.node.rsaPrivKey)
		//拼接成Prepare
		pre := Prepare{pp.Digest, pp.SequenceID, p.node.nodeID, sign}
		bPre, err := json.Marshal(pre)
		if err != nil {
			log.Panic(err)
		}
		//将消息反馈给客户端
		message := jointMessage(cReply, bPre)
		go tcpDial(message, nodeTable["N0"])
		p.isReply[pp.Digest] = true
	}
}

//客户端处理从节点的回复消息，若回复节点大于半数，则共识成功
func (p *pbft) handleReply(content []byte) {
	//使用json解析出Commit结构体
	pre := new(Reply)
	err := json.Unmarshal(content, pre)
	if err != nil {
		log.Panic(err)
	}
	fmt.Printf("主节点已接收到%s节点发来的回复消息 ... \n", pre.NodeID)
	//获取消息源节点的公钥，用于数字签名验证
	MessageNodePubKey := p.getPubKey(pre.NodeID)
	digestByte, _ := hex.DecodeString(pre.Digest)
	if _, ok := p.messagePool[pre.Digest]; !ok {
		fmt.Println("当前临时消息池无此摘要，拒绝执行commit广播")
	} else if p.sequenceID != pre.SequenceID {
		fmt.Println("消息序号对不上，拒绝执行commit广播")
	} else if !p.RsaVerySignWithSha256(digestByte, pre.Sign, MessageNodePubKey) {
		fmt.Println("节点签名验证失败！,拒绝执行commit广播")
	} else {
		p.setPrePareConfirmMap(pre.Digest, pre.NodeID, true)
		count := 0
		for range p.prePareConfirmCount[pre.Digest] {
			count++
		}
		//如果节点至少收到了一半的回复消息（不包括主节点）,并且节点没有回复过,并且已进行过commit广播，则提交信息至本地消息池
		p.lock.Lock()
		if count >= (nodeCount-1)/2 && !p.isReply[pre.Digest] {
			fmt.Println("共识完成：主节点已收到至少一半的节点(不包括主节点)发来的reply信息 ...")
				endstamp := time.Now().UnixNano()
				start, _ := time.Parse(base_format, UnixNanoToDefaultTimeStr(starttamp))
				end, _ := time.Parse(base_format, UnixNanoToDefaultTimeStr(endstamp))
				//timeall += end.Sub(start)
				writetxt(end.Sub(start).String())

		}
		p.lock.Unlock()
	}
}

func ReadAll(filePth string) ([]byte, error) {
	f, err := os.Open(filePth)
	if err != nil {
		return nil, err
	}
	return ioutil.ReadAll(f)
}

//序号累加
func (p *pbft) sequenceIDAdd() {
	p.lock.Lock()
	p.sequenceID++
	p.lock.Unlock()
}

//向除自己外的其他节点进行广播
func (p *pbft) broadcast(cmd command, content []byte) {
	for i := range nodeTable {
		if i == p.node.nodeID {
			continue
		}
		message := jointMessage(cmd, content)
		go tcpDial(message, nodeTable[i])
	}
}

//为多重映射开辟赋值
func (p *pbft) setPrePareConfirmMap(val, val2 string, b bool) {
	if _, ok := p.prePareConfirmCount[val]; !ok {
		p.prePareConfirmCount[val] = make(map[string]bool)
	}
	p.prePareConfirmCount[val][val2] = b
}

//为多重映射开辟赋值
func (p *pbft) setCommitConfirmMap(val, val2 string, b bool) {
	if _, ok := p.commitConfirmCount[val]; !ok {
		p.commitConfirmCount[val] = make(map[string]bool)
	}
	p.commitConfirmCount[val][val2] = b
}

//传入节点编号， 获取对应的公钥
func (p *pbft) getPubKey(nodeID string) []byte {
	key, err := ioutil.ReadFile("Keys/" + nodeID + "/" + nodeID + "_RSA_PUB")
	if err != nil {
		log.Panic(err)
	}
	return key
}

//传入节点编号， 获取对应的私钥
func (p *pbft) getPivKey(nodeID string) []byte {
	key, err := ioutil.ReadFile("Keys/" + nodeID + "/" + nodeID + "_RSA_PIV")
	if err != nil {
		log.Panic(err)
	}
	return key
}
