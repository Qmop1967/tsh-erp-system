import Foundation

// MARK: - API Errors
enum APIError: Error, LocalizedError {
    case invalidURL
    case noData
    case decodingError(Error)
    case networkError(Error)
    case unauthorized
    case forbidden
    case notFound
    case serverError(Int)
    case tokenExpired

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .noData: return "No data received"
        case .decodingError(let error): return "Decoding error: \(error.localizedDescription)"
        case .networkError(let error): return "Network error: \(error.localizedDescription)"
        case .unauthorized: return "Unauthorized - Please login again"
        case .forbidden: return "Access denied"
        case .notFound: return "Resource not found"
        case .serverError(let code): return "Server error: \(code)"
        case .tokenExpired: return "Session expired"
        }
    }
}

// MARK: - API Client
actor APIClient {
    static let shared = APIClient()

    private let baseURL = "https://erp.tsh.sale/api"
    private let session: URLSession
    private var retryCount = 0
    private let maxRetries = 3

    private init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)
    }

    // MARK: - Generic Request Method
    func request<T: Decodable>(
        endpoint: String,
        method: HTTPMethod = .GET,
        body: Encodable? = nil,
        queryParams: [String: String]? = nil,
        requiresAuth: Bool = true
    ) async throws -> T {
        var urlString = "\(baseURL)\(endpoint)"

        // Add query parameters
        if let params = queryParams {
            var components = URLComponents(string: urlString)
            components?.queryItems = params.map { URLQueryItem(name: $0.key, value: $0.value) }
            urlString = components?.url?.absoluteString ?? urlString
        }

        guard let url = URL(string: urlString) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        // Add authorization header
        if requiresAuth {
            if let token = KeychainService.shared.getAccessToken() {
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            } else {
                throw APIError.unauthorized
            }
        }

        // Add body
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        // Execute request with retry logic
        return try await executeWithRetry(request: request)
    }

    private func executeWithRetry<T: Decodable>(request: URLRequest) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.noData
            }

            // Handle status codes
            switch httpResponse.statusCode {
            case 200...299:
                return try JSONDecoder().decode(T.self, from: data)

            case 401:
                // Try to refresh token
                if retryCount < maxRetries {
                    retryCount += 1
                    let refreshed = try await refreshToken()
                    if refreshed {
                        // Retry with new token
                        var newRequest = request
                        if let token = KeychainService.shared.getAccessToken() {
                            newRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                        }
                        return try await executeWithRetry(request: newRequest)
                    }
                }
                NotificationCenter.default.post(name: .tokenExpired, object: nil)
                throw APIError.tokenExpired

            case 403:
                throw APIError.forbidden

            case 404:
                throw APIError.notFound

            case 500...599:
                throw APIError.serverError(httpResponse.statusCode)

            default:
                throw APIError.serverError(httpResponse.statusCode)
            }
        } catch let error as APIError {
            throw error
        } catch let error as DecodingError {
            throw APIError.decodingError(error)
        } catch {
            throw APIError.networkError(error)
        }
    }

    private func refreshToken() async throws -> Bool {
        guard let refreshToken = KeychainService.shared.getRefreshToken() else {
            return false
        }

        let endpoint = "/auth/refresh"
        let body = ["refresh_token": refreshToken]

        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            return false
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            return false
        }

        struct RefreshResponse: Decodable {
            let access_token: String
        }

        let refreshResponse = try JSONDecoder().decode(RefreshResponse.self, from: data)
        KeychainService.shared.saveAccessToken(refreshResponse.access_token)

        return true
    }
}

// MARK: - HTTP Methods
enum HTTPMethod: String {
    case GET, POST, PUT, PATCH, DELETE
}

// MARK: - Common Response Wrapper
struct APIResponse<T: Decodable>: Decodable {
    let success: Bool
    let data: T?
    let message: String?
    let message_ar: String?
}
