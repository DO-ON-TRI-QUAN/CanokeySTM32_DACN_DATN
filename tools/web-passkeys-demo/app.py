from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>CanoKey STM32 - Passkeys Web Demo (T-15)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f6f9; margin: 0; padding: 40px; display: flex; justify-content: center; }
        .container { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 480px; }
        h2 { color: #1e293b; margin-top: 0; }
        button { width: 100%; padding: 12px; margin: 10px 0; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; color: white; }
        .btn-reg { background: #2563eb; }
        .btn-reg:hover { background: #1d4ed8; }
        .btn-auth { background: #059669; }
        .btn-auth:hover { background: #047857; }
        pre { background: #f8fafc; padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto; border: 1px solid #e2e8f0; max-height: 200px; }
        input { width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box; border: 1px solid #cbd5e1; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>CanoKey Passkeys Demo (T-15)</h2>
        <p>Ứng dụng web kiểm thử xác thực Passwordless sử dụng WebAuthn API liên kết với phần cứng FIDO2.</p>
        
        <label for="username">Tên tài khoản:</label>
        <input type="text" id="username" value="trinh_bk">

        <button class="btn-reg" onclick="registerPasskey()">1. Đăng ký Passkey (Registration)</button>
        <button class="btn-auth" onclick="authenticatePasskey()">2. Đăng nhập Passkey (Authentication)</button>

        <h3>Nhật ký thực thi (Logs):</h3>
        <pre id="log">Hệ thống sẵn sàng...</pre>
    </div>

    <script>
        function log(msg) {
            const logBox = document.getElementById('log');
            logBox.innerText += "\\n[" + new Date().toLocaleTimeString() + "] " + msg;
            logBox.scrollTop = logBox.scrollHeight;
        }

        async function registerPasskey() {
            const username = document.getElementById('username').value;
            log("Bắt đầu tạo yêu cầu đăng ký (Create Credential) cho: " + username);
            
            const publicKeyCredentialCreationOptions = {
                challenge: Uint8Array.from("canokey_random_challenge_999", c => c.charCodeAt(0)),
                rp: {
                    name: "CanoKey STM32 Security Demo",
                    id: "localhost",  // Dùng localhost chuẩn cho WebAuthn
                },
                user: {
                    id: Uint8Array.from(username, c => c.charCodeAt(0)),
                    name: username,
                    displayName: username,
                },
                pubKeyCredParams: [
                    { alg: -7, type: "public-key" },  // ES256
                    { alg: -257, type: "public-key" } // RS256
                ],
                timeout: 60000,
                attestation: "direct",
                authenticatorSelection: {
                    authenticatorAttachment: "cross-platform", // Ưu tiên khóa phần cứng USB
                    userVerification: "preferred"
                }
            };

            try {
                const credential = await navigator.credentials.create({
                    publicKey: publicKeyCredentialCreationOptions
                });
                log("Đăng ký Passkey thành công!");
                log("Credential ID: " + btoa(String.fromCharCode(...new Uint8Array(credential.rawId))));
            } catch (err) {
                log("Lỗi đăng ký: " + err.message);
            }
        }

        async function authenticatePasskey() {
            log("Bắt đầu yêu cầu xác thực (Get Assertion)...");
            
            const publicKeyCredentialRequestOptions = {
                challenge: Uint8Array.from("canokey_random_challenge_999", c => c.charCodeAt(0)),
                timeout: 60000,
                rpId: "localhost",  // Dùng localhost chuẩn cho WebAuthn
                userVerification: "preferred"
            };

            try {
                const assertion = await navigator.credentials.get({
                    publicKey: publicKeyCredentialRequestOptions
                });
                log("Xác thực thành công bằng Passkey phần cứng!");
                log("ID xác thực: " + btoa(String.fromCharCode(...new Uint8Array(assertion.rawId))));
            } catch (err) {
                log("Lỗi xác thực: " + err.message);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Web Demo Server đang chạy tại: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)