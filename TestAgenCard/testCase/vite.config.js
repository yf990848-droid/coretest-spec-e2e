import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// 自定义插件：去除 crossorigin，解决偶现CSS加载跨域问题
const removeCrossOriginPlugin = () => {
  return {
    name: 'remove-crossorigin',
    transformIndexHtml(html) {
      return html
        .replace(/ crossorigin/g, '')
    }
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const base = './';
  
  return {
    base,
    plugins: [vue(), removeCrossOriginPlugin()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    build: {
      outDir: '../../test-design/webapps/testCase'
    },
    server: {
      host: "0.0.0.0",
      proxy: {
        // 代理配置示例
        '/halo-case-service/api': {
          target: 'http://10.169.63.252:8099', // 后端服务器地址
          changeOrigin: true
        }
      }
    }
  }
})
