import { vi, beforeEach, describe, it, expect } from 'vitest'
import { initWebSocket, sendMessage } from '../../services/websocketService'

let mockSocket: any

describe('WebSocket Service', () => {
  beforeEach(() => {
    mockSocket = {
      on: vi.fn().mockImplementation(function (event, callback) {
        this._callbacks = this._callbacks || {}
        this._callbacks[event] = callback
        return this
      }),
      emit: vi.fn(),
      disconnect: vi.fn(),
      connect: vi.fn(),
      _trigger: function (event, data) {
        if (this._callbacks && this._callbacks[event]) {
          this._callbacks[event](data)
        }
      },
    }

    vi.mock('socket.io-client', () => ({
      io: vi.fn(() => mockSocket),
    }))
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('异常处理', () => {
    it('应处理无效消息格式', () => {
      const setIsLoading = vi.fn()
      const setMessages = vi.fn()
      const onFullCodeReceived = vi.fn()

      initWebSocket(setMessages, onFullCodeReceived, setIsLoading)

      // 捕获消息处理函数
      const messageHandler = mockSocket.on.mock.calls.find(
        (call) => call[0] === 'message'
      )[1]

      // 测试无效JSON处理
      expect(() => messageHandler('invalid json')).toThrow(SyntaxError)
    })
  })

  describe('消息发送', () => {
    it('应正确发送消息', () => {
      const testSocket = { emit: vi.fn() }
      sendMessage(
        testSocket as any,
        'test',
        vi.fn(),
        vi.fn(),
        vi.fn(),
        'deepseek-v3' // 测试可选参数
      )
      expect(testSocket.emit).toHaveBeenCalledWith('start_project', {
        goal: 'test',
        model: 'deepseek-v3',
      })
    })
  })
})
