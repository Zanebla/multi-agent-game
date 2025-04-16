import MCPClient from './MCPClient'
import Agent from './Agent'
import path from 'path'
import EmbeddingRetriever from './EmbeddingRetriever'
import fs from 'fs'
import { logTitle } from './utils'

// const URL = 'https://news.ycombinator.com/'
const outPath = path.join(process.cwd(), 'output')
const TASK = `
告诉我diavolo的信息,先从我给你的context中找到相关信息,然后让他变成现代的程序员，描绘他的个人风格,
把个人风格和他的基本信息保存到${outPath}\\diavolo.md,输出一个md文件
`
// const TASK = `
// 告诉我dio的信息,先从我给你的context中找到相关信息,然后让他变成现代的产品经理,描绘他的个人风格,
// 把个人风格和他的基本信息保存到${outPath}\\dio.md,输出一个md文件
// `

const fetchMCP = new MCPClient('mcp-server-fetch', 'uvx', ['mcp-server-fetch'])
const fileMCP = new MCPClient('mcp-server-file', 'npx', [
  '-y',
  '@modelcontextprotocol/server-filesystem',
  outPath,
])

async function main() {
  // const baseAgent = new Agent('gpt-4o', [fetchMCP, fileMCP], '', '')
  // await baseAgent.init()
  // try {
  //   // 第一次爬取 - 迪奥布兰度
  //   const response1 = await baseAgent.invoke(
  //     `新建${outPath}\\knowledge\\dio.md，爬取 https://zanebla.github.io/posts/0.html
  //     并将详细信息（简介，角色性格，角色能力，替身，经典台词）逐条保存到 ${outPath}\\knowledge\\dio.md`
  //   )
  //   console.log(response1)

  //   // 第二次爬取 - 迪亚波罗
  //   const response2 = await baseAgent.invoke(
  //     `新建 ${outPath}\\knowledge\\diavolo.md，爬取 https://zanebla.github.io/posts/cfa4db3c.html
  //     并将详细信息（简介，角色性格，角色能力，替身，经典台词）逐条保存到 ${outPath}\\knowledge\\diavolo.md `
  //   )
  //   console.log(response2)
  // } finally {
  //   await baseAgent.close()
  // }

  const context = await retrieveContext()

  const mainAgent = new Agent('gpt-4o', [fetchMCP, fileMCP], '', context)
  await mainAgent.init()

  try {
    const response = await mainAgent.invoke(TASK, false)
    console.log(response)
  } finally {
    await mainAgent.close()
  }
}

main()

async function retrieveContext() {
  // RAG
  const embeddingRetriever = new EmbeddingRetriever('BAAI/bge-m3')
  const knowledgeDir = path.join(outPath, 'knowledge')
  const files = fs.readdirSync(knowledgeDir)
  for await (const file of files) {
    const content = fs.readFileSync(path.join(knowledgeDir, file), 'utf-8')
    await embeddingRetriever.embedDocument(content)
  }
  const context = (await embeddingRetriever.retrieve(TASK, 1)).join('\n')
  logTitle('CONTEXT')
  console.log(context)
  return context
}
