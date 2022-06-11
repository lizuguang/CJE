package main

import (
	"bufio"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/big"
	"os"
	"strconv"
	"strings"
	"time"
)
func clientSendMessageAndListen(){
	//开启客户端的本地监听（主要用来接收节点的reply信息）
	go clientTcpListen()      //go启动并行线程
	fmt.Printf("客户端开启监听，地址：%s\n", clientAddr)

	fmt.Println(" ---------------------------------------------------------------------------------")
	fmt.Println("|  已进入PBFT测试Demo客户端，请启动全部节点后再发送消息！ :)  |")
	fmt.Println(" ---------------------------------------------------------------------------------")
	//fmt.Println("请在下方输入要存入节点的信息：")
	//读取txt中的文件
	//首先通过命令行获取用户输入
	/*stdReader := bufio.NewReader(os.Stdin)
		da, err := stdReader.ReadString('\n')
		if err != nil {
			fmt.Println("Error reading from stdin")
			panic(err)
		}
		fmt.Println(da)*/
	data, err := ioutil.ReadFile("E:\\go_code\\blockchain_consensus_algorithm\\proposed\\block.txt")
	if err != nil {
		fmt.Println("File reading error", err)
		return
	}
	for i := 0; i < 100; i++{
		time.Sleep(time.Second * 1)
		r := new(Request)
		r.ClientAddr = clientAddr
		r.Message.ID = getRandom()
		//消息内容就是用户的输入
		r.Message.Content = strings.TrimSpace(string(data))
		r.Timestamp = time.Now().UnixNano()
		//writestart()

		br, err := json.Marshal(r)
		if err != nil {
			log.Panic(err)
		}
		//fmt.Println(string(br))
		content := jointMessage(cRequest, br)
		//默认N0为主节点，直接把请求信息发送至N0
		tcpDial(content, nodeTable["N0"])
		}
	}

//返回一个十位数的随机数，作为msgid
func getRandom() int {
	x := big.NewInt(10000000000)
	for {
		result, err := rand.Int(rand.Reader, x)
		if err != nil {
			log.Panic(err)
		}
		if result.Int64() > 1000000000 {
			return int(result.Int64())
		}
	}
}
func writestart(){

	filePath := "E:\\go_code\\blockchain_consensus_algorithm\\proposed\\startstamp.txt"
	file, err := os.OpenFile(filePath, os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		fmt.Printf("open file err=%v\n", err)
		return
	}
	// 及时关闭 file 句柄
	defer file.Close()
	writer := bufio.NewWriter(file)
	writer.WriteString(strconv.FormatInt( time.Now().UnixNano(), 10))
	// 因为 writer 是带缓存，因此在调用 WriterString 方法时，其实内容是先写入到缓存的,所以需要调用 Flush 方法，将缓冲的数据真正写入到文件中， 否则文件中会没有数据!!!
	writer.Flush()
}