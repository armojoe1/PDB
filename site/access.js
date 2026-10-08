// Sign-in settings for the dashboard. The real gate is Netlify's team login;
// this passphrase is the second, cosmetic one on the ODNI screen.
// To change it: python3 -c "import hashlib;print(hashlib.sha256(b'NEW-PASSPHRASE').hexdigest())"
// and paste the result below. Leave it empty ("") to accept any passphrase.
window.PDB_ACCESS = { passphraseSha256: "0697370ddf8056209fe5307bbd58dc5cbe1a5c24972faea01e68de79e2ba5d71" };
