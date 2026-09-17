# purevel-legal

Páginas públicas de https://bpurevel.com: términos, privacidad, centro de ayuda
y eliminación de cuenta. HTML estático servido con GitHub Pages.

## De dónde sale el texto

De un solo archivo: `terminos-privacidad-y-centro-de-ayuda.md` en el vault de
Obsidian. Los `index.html` se generan; no se editan a mano.

```sh
python3 -m venv .venv && .venv/bin/pip install markdown
.venv/bin/python build.py            # usa la ruta del vault por defecto
.venv/bin/python build.py otro.md    # o una ruta explícita
```

`build.py` explica qué partes se publican y cuáles no.

## Publicar

1. Repo **público** en GitHub con el contenido de esta carpeta.
2. Settings → Pages → Deploy from a branch → `master` / root.
3. Custom domain: `bpurevel.com` (ya está en `CNAME`). Verificar el dominio en
   Settings → Pages de la cuenta.
4. DNS en Cloudflare (los `A`/`AAAA` de `@` con proxy desde 2026-09-17, ver abajo):
   - `A @` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `AAAA @` (opcional) → `2606:50c0:8000::153` … `2606:50c0:8003::153`
   - `CNAME www` → `<usuario>.github.io`
   - No tocar los registros MX ni los de Resend.
5. Cuando GitHub emita el certificado: **Enforce HTTPS**.

URL de privacidad para AdMob y las tiendas: https://bpurevel.com/privacidad/

## Lo que no sale de `build.py`

- `og-default.png` (1200×630): la imagen de la vista previa cuando la
  publicación compartida no tiene foto. La usa la edge function `og-preview`.
- `.well-known/assetlinks.json`: le dice a Android que la app `com.purevel.app`
  puede abrir los enlaces de este dominio sin pasar por el navegador. Hoy trae
  la huella de la clave de **debug** de la máquina de desarrollo. Cuando la app
  se firme para Play, agregar la huella SHA-256 que muestra Play Console
  (Integridad de la app → Firma de apps), no la del keystore local.
- `app-ads.txt`: AdMob.

## Enlaces compartidos (`/post/…`, `/battle/…`)

No los sirve GitHub Pages. Los atiende el Worker de Cloudflare
`purevel-share-links` (código en el repo de la app, `cloudflare/share-links/`),
que responde con la edge function `og-preview`. Para eso los `A`/`AAAA` de `@`
van con proxy (nube naranja) y la zona en SSL **Full**. No usar *Full (strict)*:
con el proxy delante, GitHub puede no renovar su certificado y *Full* lo sigue
aceptando.
