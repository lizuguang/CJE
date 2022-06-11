package main

import (
	"log"
	"os"
)

const nodeCount = 20

//客户端的监听地址
var clientAddr = "127.0.0.1:8888"
//节点池，主要用来存储监听地址
var nodeTable map[string]string
func main() {
	//为四个节点生成公私钥
	genRsaKeys()
	nodeTable = map[string]string{
		"N0": "127.0.0.1:8000",
		"N1": "127.0.0.1:8001",
		"N2": "127.0.0.1:8002",
		"N3": "127.0.0.1:8003",
		"N4": "127.0.0.1:8004",
		"N5": "127.0.0.1:8005",
		"N6": "127.0.0.1:8006",
		"N7": "127.0.0.1:8007",
		"N8": "127.0.0.1:8008",
		"N9": "127.0.0.1:8009",
		"N10": "127.0.0.1:8010",
		"N11": "127.0.0.1:8011",
		"N12": "127.0.0.1:8012",
		"N13": "127.0.0.1:8013",
		"N14": "127.0.0.1:8014",
		"N15": "127.0.0.1:8015",
		"N16": "127.0.0.1:8016",
		"N17": "127.0.0.1:8017",
		"N18": "127.0.0.1:8018",
		"N19": "127.0.0.1:8019",
	}
	if len(os.Args) != 2 {
		log.Panic("输入的参数有误！")
	}
	nodeID := os.Args[1]
	if nodeID == "client" {
		clientSendMessageAndListen() //启动客户端程序
	} else if addr, ok := nodeTable[nodeID]; ok {
		p := NewPBFT(nodeID, addr)
		go p.tcpListen() //启动节点
	} else {
		log.Fatal("无此节点编号！")
	}
	select {}
}
