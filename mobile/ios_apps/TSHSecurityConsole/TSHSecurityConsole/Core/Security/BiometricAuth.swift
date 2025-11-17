import LocalAuthentication
import Foundation

class BiometricAuth {
    static let shared = BiometricAuth()

    private let context = LAContext()
    private(set) var biometricType: BiometricType = .none

    enum BiometricType {
        case none
        case touchID
        case faceID
    }

    enum BiometricError: Error, LocalizedError {
        case notAvailable
        case notEnrolled
        case authFailed
        case userCancelled
        case systemCancel
        case passcodeNotSet
        case biometryLockout

        var errorDescription: String? {
            switch self {
            case .notAvailable: return "Biometric authentication is not available"
            case .notEnrolled: return "No biometric data enrolled"
            case .authFailed: return "Authentication failed"
            case .userCancelled: return "Authentication cancelled"
            case .systemCancel: return "System cancelled authentication"
            case .passcodeNotSet: return "Passcode is not set"
            case .biometryLockout: return "Biometric authentication is locked out"
            }
        }
    }

    private init() {
        checkBiometricType()
    }

    private func checkBiometricType() {
        var error: NSError?

        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            switch context.biometryType {
            case .faceID:
                biometricType = .faceID
            case .touchID:
                biometricType = .touchID
            default:
                biometricType = .none
            }
        } else {
            biometricType = .none
        }
    }

    var isBiometricAvailable: Bool {
        return biometricType != .none
    }

    var biometricName: String {
        switch biometricType {
        case .faceID: return "Face ID"
        case .touchID: return "Touch ID"
        case .none: return "Biometric"
        }
    }

    var biometricIcon: String {
        switch biometricType {
        case .faceID: return "faceid"
        case .touchID: return "touchid"
        case .none: return "lock"
        }
    }

    func authenticate(reason: String) async throws -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "Cancel"

        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            if let err = error {
                throw mapLAError(err)
            }
            throw BiometricError.notAvailable
        }

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
            return success
        } catch let error as LAError {
            throw mapLAError(error)
        }
    }

    private func mapLAError(_ error: NSError) -> BiometricError {
        guard let laError = error as? LAError else {
            return .authFailed
        }

        switch laError.code {
        case .biometryNotAvailable:
            return .notAvailable
        case .biometryNotEnrolled:
            return .notEnrolled
        case .authenticationFailed:
            return .authFailed
        case .userCancel:
            return .userCancelled
        case .systemCancel:
            return .systemCancel
        case .passcodeNotSet:
            return .passcodeNotSet
        case .biometryLockout:
            return .biometryLockout
        default:
            return .authFailed
        }
    }
}
