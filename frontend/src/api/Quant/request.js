import { HttpClient } from '../request.js'


export class quantClient extends HttpClient {
  handleRequest(config) {
   
    return config
  }

  handleResponse(response) {
    const payload = super.handleResponse(response)

    return payload
  }
}

const request = new quantClient({
  baseURL: 'http://127.0.0.1:8001',
  timeout: 15000,
})

export const service = request.service

export default request
