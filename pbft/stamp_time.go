package main

import (
	"os"
	"time"
)

const (
	YearMonthDay     = "2006-01-02"
	HourMinuteSecond = "15:04:05.000000000"
	DefaultLayout    = YearMonthDay + " " + HourMinuteSecond
)

func UnixNanoToDefaultTimeStr(nano int64) string {
	return UnixNanoToTimeStr(nano, DefaultLayout)
}
// 纳秒级时间戳转指定格式日期字符串
func UnixNanoToTimeStr(nano int64, layout string) string {
	return TimeToStr(UnixNanoToTime(nano), layout)
}
func TimeToStr(t time.Time, layout string) string {
	return t.Format(layout)
}
func UnixNanoToTime(nano int64) time.Time {
	return time.Unix(nano/(1000*1000*1000), nano%(1000*1000*1000))
}

//写入txt文件
func writetxt(content string) {
	f, err := os.OpenFile("E:\\go_code\\blockchain_consensus_algorithm\\pbft\\PBFT_Time.txt", os.O_WRONLY, 0644)
	content = content + "\n"
	if err != nil {
		// 打开文件失败处理
	} else {
		// 查找文件末尾的偏移量
		n, _ := f.Seek(0, 2)

		// 从末尾的偏移量开始写入内容
		_, err = f.WriteAt([]byte(content), n)
	}
}