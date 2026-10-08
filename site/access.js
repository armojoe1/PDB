// Sign-in settings for the dashboard. The real gate is Netlify's team login;
// this is the second, cosmetic one on the ODNI screen.
// To change the passphrase: python3 -c "import hashlib;print(hashlib.sha256(b'NEW-PASSPHRASE').hexdigest())"
// and paste the result into passphraseSha256. Leave it empty ("") to accept any passphrase;
// leave userId empty to accept any user ID.
window.PDB_ACCESS = { userId: "joearmitage", passphraseSha256: "9594db3bed0f46fdf4c12978ad7905ad510f366dece7875ba57f9c13cbebdd60" };
