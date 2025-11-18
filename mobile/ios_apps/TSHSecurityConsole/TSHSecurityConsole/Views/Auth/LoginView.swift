import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @EnvironmentObject var appState: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var rememberMe = true
    @State private var showBiometricOption = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                // Logo and Title
                VStack(spacing: 12) {
                    Image(systemName: "shield.checkered")
                        .font(.system(size: 80))
                        .foregroundColor(.blue)

                    Text(appState.isArabic ? "وحدة أمان TSH" : "TSH Security Console")
                        .font(.largeTitle)
                        .fontWeight(.bold)

                    Text(appState.isArabic ? "الوصول للمدير/المالك فقط" : "Owner/Director Access Only")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .padding(.top, 40)

                // Login Form
                VStack(spacing: 16) {
                    TextField(
                        appState.isArabic ? "البريد الإلكتروني" : "Email",
                        text: $email
                    )
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .autocapitalization(.none)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)

                    SecureField(
                        appState.isArabic ? "كلمة المرور" : "Password",
                        text: $password
                    )
                    .textContentType(.password)
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)

                    Toggle(
                        appState.isArabic ? "تذكرني" : "Remember Me",
                        isOn: $rememberMe
                    )
                    .toggleStyle(.checkbox)
                }
                .padding(.horizontal)

                // Error Message
                if let error = authViewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }

                // Login Button
                Button(action: {
                    Task {
                        await authViewModel.login(email: email, password: password)
                    }
                }) {
                    if authViewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text(appState.isArabic ? "تسجيل الدخول" : "Login")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
                .disabled(email.isEmpty || password.isEmpty || authViewModel.isLoading)
                .padding(.horizontal)

                // Biometric Login
                if BiometricAuth.shared.isBiometricAvailable && KeychainService.shared.getUserEmail() != nil {
                    Button(action: {
                        Task {
                            await authViewModel.loginWithBiometrics()
                        }
                    }) {
                        HStack {
                            Image(systemName: BiometricAuth.shared.biometricIcon)
                            Text(appState.isArabic ? "تسجيل الدخول بـ" : "Login with") + Text(" \(BiometricAuth.shared.biometricName)")
                        }
                    }
                    .padding()
                }

                Spacer()

                // Language Toggle
                Button(action: {
                    appState.toggleLanguage()
                }) {
                    HStack {
                        Image(systemName: "globe")
                        Text(appState.isArabic ? "English" : "العربية")
                    }
                }
                .padding(.bottom)
            }
            .onAppear {
                // Pre-fill email from saved credentials (for convenience)
                if let savedEmail = KeychainService.shared.getUserEmail(), email.isEmpty {
                    email = savedEmail
                }
                // Clear any stale error messages
                authViewModel.errorMessage = nil
            }
        }
    }
}

// Custom checkbox toggle style
struct CheckboxToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label

            Spacer()

            Image(systemName: configuration.isOn ? "checkmark.square.fill" : "square")
                .foregroundColor(configuration.isOn ? .blue : .gray)
                .onTapGesture {
                    configuration.isOn.toggle()
                }
        }
    }
}

extension ToggleStyle where Self == CheckboxToggleStyle {
    static var checkbox: CheckboxToggleStyle { CheckboxToggleStyle() }
}

#Preview {
    LoginView()
        .environmentObject(AuthViewModel())
        .environmentObject(AppState())
}
