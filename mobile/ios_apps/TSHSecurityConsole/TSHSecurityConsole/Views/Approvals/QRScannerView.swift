import SwiftUI
import AVFoundation

struct QRScannerView: View {
    @Environment(\.dismiss) var dismiss
    @EnvironmentObject var appState: AppState
    @StateObject private var scanner = QRCodeScanner()
    var onScan: (String) -> Void

    var body: some View {
        NavigationStack {
            ZStack {
                // Camera preview
                CameraPreviewView(scanner: scanner)
                    .edgesIgnoringSafeArea(.all)

                // Overlay
                VStack {
                    Spacer()

                    // Scan frame
                    RoundedRectangle(cornerRadius: 20)
                        .stroke(Color.white, lineWidth: 3)
                        .frame(width: 250, height: 250)
                        .overlay {
                            if scanner.isScanning {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                    .scaleEffect(1.5)
                            }
                        }

                    Spacer()

                    // Instructions
                    Text(appState.isArabic ? "وجّه الكاميرا نحو رمز QR" : "Point camera at QR code")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(10)
                        .padding(.bottom, 50)
                }

                // Error message
                if let error = scanner.error {
                    VStack {
                        Spacer()
                        Text(error)
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.red)
                            .cornerRadius(10)
                            .padding()
                    }
                }
            }
            .navigationTitle(appState.isArabic ? "مسح رمز QR" : "Scan QR Code")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(appState.isArabic ? "إلغاء" : "Cancel") {
                        scanner.stopScanning()
                        dismiss()
                    }
                    .foregroundColor(.white)
                }
            }
            .toolbarBackground(.hidden, for: .navigationBar)
        }
        .onAppear {
            scanner.startScanning { code in
                onScan(code)
            }
        }
        .onDisappear {
            scanner.stopScanning()
        }
    }
}

// MARK: - QR Code Scanner
class QRCodeScanner: NSObject, ObservableObject, AVCaptureMetadataOutputObjectsDelegate {
    @Published var isScanning = false
    @Published var error: String?

    var captureSession: AVCaptureSession?
    var previewLayer: AVCaptureVideoPreviewLayer?
    private var onCodeScanned: ((String) -> Void)?

    func startScanning(onScan: @escaping (String) -> Void) {
        self.onCodeScanned = onScan
        isScanning = false
        error = nil

        guard let captureDevice = AVCaptureDevice.default(for: .video) else {
            error = "Camera not available"
            return
        }

        captureSession = AVCaptureSession()

        do {
            let input = try AVCaptureDeviceInput(device: captureDevice)
            captureSession?.addInput(input)

            let metadataOutput = AVCaptureMetadataOutput()
            captureSession?.addOutput(metadataOutput)
            metadataOutput.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
            metadataOutput.metadataObjectTypes = [.qr]

            previewLayer = AVCaptureVideoPreviewLayer(session: captureSession!)
            previewLayer?.videoGravity = .resizeAspectFill

            DispatchQueue.global(qos: .userInitiated).async { [weak self] in
                self?.captureSession?.startRunning()
            }
        } catch {
            self.error = error.localizedDescription
        }
    }

    func stopScanning() {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.captureSession?.stopRunning()
        }
    }

    func metadataOutput(_ output: AVCaptureMetadataOutput,
                        didOutput metadataObjects: [AVMetadataObject],
                        from connection: AVCaptureConnection) {
        guard !isScanning else { return }

        if let metadataObject = metadataObjects.first {
            guard let readableObject = metadataObject as? AVMetadataMachineReadableCodeObject else { return }
            guard let stringValue = readableObject.stringValue else { return }

            // Haptic feedback
            AudioServicesPlaySystemSound(SystemSoundID(kSystemSoundID_Vibrate))

            isScanning = true
            onCodeScanned?(stringValue)
        }
    }
}

// MARK: - Camera Preview View
struct CameraPreviewView: UIViewRepresentable {
    @ObservedObject var scanner: QRCodeScanner

    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: UIScreen.main.bounds)

        if let previewLayer = scanner.previewLayer {
            previewLayer.frame = view.layer.bounds
            view.layer.addSublayer(previewLayer)
        }

        return view
    }

    func updateUIView(_ uiView: UIView, context: Context) {
        if let previewLayer = scanner.previewLayer {
            previewLayer.frame = uiView.layer.bounds
        }
    }
}

#Preview {
    QRScannerView { code in
        print("Scanned: \(code)")
    }
    .environmentObject(AppState())
}
