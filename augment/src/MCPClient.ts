import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { Tool } from '@modelcontextprotocol/sdk/types.js'

export default class MCPClient {
  private mcp: Client
  private command: string
  private args: string[]
  private transport: StdioClientTransport | null = null
  private tools: Tool[] = []
  private isConnected = false

  constructor(name: string, command: string, args: string[], version?: string) {
    this.mcp = new Client({ name, version: version || '0.0.1' })
    this.command = command
    this.args = args
  }

  public async init() {
    await this.connectToServer()
  }

  public async close() {
    if (this.isConnected) {
      await this.mcp.close()
      this.isConnected = false
      this.transport = null
    }
  }

  public getTools() {
    return this.tools
  }

  public async callTool(name: string, params: Record<string, any>) {
    if (!this.isConnected) {
      await this.reconnect() // 自动重连
    }
    return this.mcp.callTool({
      name,
      arguments: params,
    })
  }

  private async reconnect() {
    try {
      await this.close()
      await this.connectToServer()
    } catch (e) {
      console.error('MCP重连失败:', e)
      throw e
    }
  }

  private async connectToServer() {
    try {
      this.transport = new StdioClientTransport({
        command: this.command,
        args: this.args,
      })
      await this.mcp.connect(this.transport)
      this.isConnected = true

      const toolsResult = await this.mcp.listTools()
      this.tools = toolsResult.tools.map((tool) => {
        return {
          name: tool.name,
          description: tool.description,
          inputSchema: tool.inputSchema,
        }
      })
      console.log(
        'Connected to server with tools:',
        this.tools.map(({ name }) => name)
      )
    } catch (e) {
      console.log('Failed to connect to MCP server: ', e)
      throw e
    }
  }
}
