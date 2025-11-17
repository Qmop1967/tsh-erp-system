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
    case serverMessage(String)  // Custom server error message

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
        case .serverMessage(let message): return message
        }
    }
}

// MARK: - Environment Configuration
enum APIEnvironment {
    case development  // Local machine
    case staging      // Staging server
    case production   // Production server

    var baseURL: String {
        switch self {
        case .development:
            // Use Mac's local IP (update if your IP changes)
            return "http://192.168.68.73:8000/api"
        case .staging:
            return "https://staging.erp.tsh.sale/api"
        case .production:
            return "https://erp.tsh.sale/api"
        }
    }
}

// MARK: - API Client
actor APIClient {
    static let shared = APIClient()

    // ⚠️ Change this to switch environments
    private static let currentEnvironment: APIEnvironment = .production

    private let baseURL: String
    private let session: URLSession
    private var retryCount = 0
    private let maxRetries = 3

    private init() {
        self.baseURL = APIClient.currentEnvironment.baseURL

        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 60
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)

        #if DEBUG
        print("🔗 APIClient initialized with environment: \(APIClient.currentEnvironment)")
        print("📍 Base URL: \(self.baseURL)")
        #endif
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
            #if DEBUG
            print("❌ [APIClient] Invalid URL: \(urlString)")
            #endif
            throw APIError.invalidURL
        }

        #if DEBUG
        print("🌐 [APIClient] \(method.rawValue) \(endpoint)")
        if let params = queryParams, !params.isEmpty {
            print("   Query params: \(params)")
        }
        #endif

        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        // Add authorization header
        if requiresAuth {
            #if DEBUG
            print("   🔐 Requires auth - checking for token...")
            #endif

            if let token = KeychainService.shared.getAccessToken() {
                #if DEBUG
                print("   ✅ Token found (length: \(token.count), prefix: \(String(token.prefix(20)))...)")
                #endif
                request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
            } else {
                #if DEBUG
                print("   ❌ NO TOKEN FOUND IN KEYCHAIN!")
                let diagnostics = KeychainService.shared.diagnosticInfo()
                print("   📊 Keychain diagnostics: \(diagnostics)")
                #endif
                throw APIError.unauthorized
            }
        } else {
            #if DEBUG
            print("   🔓 No auth required")
            #endif
        }

        // Add body
        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
            #if DEBUG
            print("   📦 Request body attached")
            #endif
        }

        // Execute request with retry logic
        return try await executeWithRetry(request: request, shouldRefreshToken: requiresAuth)
    }

    private func executeWithRetry<T: Decodable>(request: URLRequest, shouldRefreshToken: Bool = true) async throws -> T {
        do {
            let (data, response) = try await session.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse else {
                #if DEBUG
                print("   ❌ Invalid response type")
                #endif
                throw APIError.noData
            }

            #if DEBUG
            print("   📥 Response status: \(httpResponse.statusCode)")
            #endif

            // Handle status codes
            switch httpResponse.statusCode {
            case 200...299:
                #if DEBUG
                print("   ✅ Request successful")
                #endif

                // Check if response is empty
                guard !data.isEmpty else {
                    #if DEBUG
                    print("   ⚠️ Empty response data")
                    #endif
                    throw APIError.noData
                }

                do {
                    let decoded = try JSONDecoder().decode(T.self, from: data)
                    #if DEBUG
                    print("   ✅ Response decoded successfully")
                    #endif
                    return decoded
                } catch let decodingError as DecodingError {
                    // Log the actual response for debugging
                    #if DEBUG
                    if let jsonString = String(data: data, encoding: .utf8) {
                        print("   ⚠️ JSON Decoding Error. Response: \(jsonString.prefix(500))...")
                        print("   ⚠️ Error details: \(decodingError)")
                    }
                    #endif
                    throw APIError.decodingError(decodingError)
                }

            case 401:
                #if DEBUG
                print("   ⚠️ 401 Unauthorized response")
                if let errorMessage = parseErrorMessage(from: data) {
                    print("   📝 Server message: \(errorMessage)")
                }
                #endif

                // Only try to refresh token if this was an authenticated request
                if shouldRefreshToken && retryCount < maxRetries {
                    #if DEBUG
                    print("   🔄 Attempting token refresh (retry \(retryCount + 1)/\(maxRetries))...")
                    #endif
                    retryCount += 1
                    let refreshed = try await refreshToken()
                    if refreshed {
                        #if DEBUG
                        print("   ✅ Token refreshed, retrying request...")
                        #endif
                        // Retry with new token
                        var newRequest = request
                        if let token = KeychainService.shared.getAccessToken() {
                            newRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
                        }
                        return try await executeWithRetry(request: newRequest, shouldRefreshToken: shouldRefreshToken)
                    } else {
                        #if DEBUG
                        print("   ❌ Token refresh failed")
                        #endif
                    }
                }

                // Try to extract error message from response
                if let errorMessage = parseErrorMessage(from: data) {
                    #if DEBUG
                    print("   ❌ Throwing server message: \(errorMessage)")
                    #endif
                    throw APIError.serverMessage(errorMessage)
                }

                // If this was a non-auth request (like login), return unauthorized not tokenExpired
                if !shouldRefreshToken {
                    #if DEBUG
                    print("   ❌ Throwing unauthorized (non-auth request)")
                    #endif
                    throw APIError.unauthorized
                }

                #if DEBUG
                print("   ❌ Token expired, posting notification")
                #endif
                NotificationCenter.default.post(name: .tokenExpired, object: nil)
                throw APIError.tokenExpired

            case 403:
                if let errorMessage = parseErrorMessage(from: data) {
                    throw APIError.serverMessage(errorMessage)
                }
                throw APIError.forbidden

            case 404:
                if let errorMessage = parseErrorMessage(from: data) {
                    throw APIError.serverMessage(errorMessage)
                }
                throw APIError.notFound

            case 500...599:
                if let errorMessage = parseErrorMessage(from: data) {
                    throw APIError.serverMessage(errorMessage)
                }
                throw APIError.serverError(httpResponse.statusCode)

            default:
                if let errorMessage = parseErrorMessage(from: data) {
                    throw APIError.serverMessage(errorMessage)
                }
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

    private func parseErrorMessage(from data: Data) -> String? {
        // Try to parse error response format: {"success": false, "error": {"message": "..."}}
        struct ErrorResponse: Decodable {
            let success: Bool?
            let error: ErrorDetail?
            let message: String?
            let detail: String?

            struct ErrorDetail: Decodable {
                let message: String?
                let code: String?
            }
        }

        if let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data) {
            // Check for nested error.message
            if let message = errorResponse.error?.message {
                return message
            }
            // Check for top-level message
            if let message = errorResponse.message {
                return message
            }
            // Check for detail (FastAPI validation errors)
            if let detail = errorResponse.detail {
                return detail
            }
        }

        // Try to parse as string
        if let stringMessage = String(data: data, encoding: .utf8), !stringMessage.isEmpty {
            // Only return if it looks like a message (not JSON)
            if !stringMessage.hasPrefix("{") && !stringMessage.hasPrefix("[") {
                return stringMessage
            }
        }

        return nil
    }

    private func refreshToken() async throws -> Bool {
        #if DEBUG
        print("   🔄 [APIClient] Attempting to refresh token...")
        #endif

        guard let refreshToken = KeychainService.shared.getRefreshToken() else {
            #if DEBUG
            print("   ❌ [APIClient] No refresh token available in Keychain")
            #endif
            return false
        }

        let endpoint = "/auth/refresh"
        let body = ["refresh_token": refreshToken]

        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            #if DEBUG
            print("   ❌ [APIClient] Invalid refresh URL")
            #endif
            return false
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)

        #if DEBUG
        print("   🌐 [APIClient] Sending refresh request to \(endpoint)")
        #endif

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            #if DEBUG
            print("   ❌ [APIClient] Invalid refresh response type")
            #endif
            return false
        }

        #if DEBUG
        print("   📥 [APIClient] Refresh response status: \(httpResponse.statusCode)")
        #endif

        guard httpResponse.statusCode == 200 else {
            #if DEBUG
            print("   ❌ [APIClient] Refresh failed with status: \(httpResponse.statusCode)")
            if let responseString = String(data: data, encoding: .utf8) {
                print("   📝 Response: \(responseString.prefix(200))")
            }
            #endif
            return false
        }

        struct RefreshResponse: Decodable {
            let access_token: String
        }

        do {
            let refreshResponse = try JSONDecoder().decode(RefreshResponse.self, from: data)
            let saved = KeychainService.shared.saveAccessToken(refreshResponse.access_token)

            #if DEBUG
            if saved {
                print("   ✅ [APIClient] New access token saved successfully")
            } else {
                print("   ❌ [APIClient] Failed to save new access token")
            }
            #endif

            return saved
        } catch {
            #if DEBUG
            print("   ❌ [APIClient] Failed to decode refresh response: \(error)")
            #endif
            return false
        }
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
