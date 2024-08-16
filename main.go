package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/go-ini/ini"
	"github.com/spf13/pflag"
)

const defaultConf = `[proxy]
host = 127.0.0.1
port = 7890

[log]
level = INFO
`

type GitProxy struct {
	args      []string
	proxyConf map[string]string
}

func NewGitProxy(args []string, host string, port int) *GitProxy {
	proxyURL := fmt.Sprintf("http://%s:%d", host, port)
	return &GitProxy{
		args: args,
		proxyConf: map[string]string{
			"http.proxy":  proxyURL,
			"https.proxy": proxyURL,
		},
	}
}

func (gp *GitProxy) setProxy() {
	for k, v := range gp.proxyConf {
		exec.Command("git", "config", "--global", k, v).Run()
	}
	log.Println("Proxy set successfully")
}

func (gp *GitProxy) unsetProxy() {
	for k := range gp.proxyConf {
		exec.Command("git", "config", "--global", "--unset", k).Run()
	}
	log.Println("Proxy unset successfully")
}

func (gp *GitProxy) getProxy() {
	for k := range gp.proxyConf {
		out, _ := exec.Command("git", "config", "--global", "--get", k).Output()
		log.Printf("%s=%s", k, strings.TrimSpace(string(out)))
	}
}

func (gp *GitProxy) executeGitCommand() {
	// 设置代理
	gp.setProxy()
	defer gp.unsetProxy()

	// 捕获中断信号
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	done := make(chan error, 1)

	go func() {
		gitCmd := append([]string{}, gp.args...)
		cmd := exec.Command("git", gitCmd...)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		done <- cmd.Run()
	}()

	select {
	case err := <-done:
		if err != nil {
			gp.unsetProxy()
			log.Fatalf("Failed to execute git command: %v", err)
		}
	case sig := <-sigChan:
		log.Printf("Received signal: %v, cleaning up...", sig)
	}

}

func createDefaultConf(confFile string) {
	f, err := os.Create(confFile)
	if err != nil {
		log.Fatalf("Failed to create config file: %v", err)
	}
	defer f.Close()

	writer := bufio.NewWriter(f)
	_, err = writer.WriteString(defaultConf)
	if err != nil {
		log.Fatalf("Failed to write default config: %v", err)
	}
	writer.Flush()
	log.Printf("Created default config file at %s", confFile)
}

func readConf(confFile string) (string, int, string) {
	cfg, err := ini.Load(confFile)
	if err != nil {
		log.Fatalf("Failed to read config file: %v", err)
	}

	host := cfg.Section("proxy").Key("host").String()
	port, err := cfg.Section("proxy").Key("port").Int()
	if err != nil {
		log.Fatalf("Invalid port in config file: %v", err)
	}
	logLevel := cfg.Section("log").Key("level").String()

	return host, port, logLevel
}

func initConf() (string, int, string) {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Fatalf("Failed to get home directory: %v", err)
	}
	confDir := filepath.Join(homeDir, ".gitc")
	if _, err := os.Stat(confDir); os.IsNotExist(err) {
		os.MkdirAll(confDir, os.ModePerm)
	}

	confFile := filepath.Join(confDir, "gitc.ini")
	if _, err := os.Stat(confFile); os.IsNotExist(err) {
		createDefaultConf(confFile)
	}

	return readConf(confFile)
}

func main() {
	setProxy := pflag.BoolP("set-proxy", "s", false, "Set proxy")
	unsetProxy := pflag.BoolP("unset-proxy", "u", false, "Unset proxy")
	getProxy := pflag.BoolP("get-proxy", "g", false, "Get proxy")
	help := pflag.BoolP("help", "h", false, "Show this help message")
	pflag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage: %s [OPTIONS] [GIT_COMMAND]\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "\nOptions:\n")
		pflag.PrintDefaults()
		fmt.Fprintf(os.Stderr, "\nGit Commands:\n")
		fmt.Fprintf(os.Stderr, "  <git_command>       Any other git command, such as clone: `gitc clone <your repo>`\n")
	}
	pflag.Parse()

	if *help {
		pflag.Usage()
		return
	}

	host, port, logLevel := initConf()
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	if logLevel == "DEBUG" {
		log.SetFlags(log.LstdFlags | log.Lshortfile | log.Lmicroseconds)
	}

	args := pflag.Args()
	proxy := NewGitProxy(args, host, port)

	switch {
	case *setProxy:
		proxy.setProxy()
	case *unsetProxy:
		proxy.unsetProxy()
	case *getProxy:
		proxy.getProxy()
	default:
		proxy.executeGitCommand()
	}

}
