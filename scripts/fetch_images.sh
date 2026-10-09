#!/bin/bash
DIR="$(dirname "$0")/../app/static/images"
mkdir -p "$DIR"

products=(
 p1:headphones p2:smartwatch p3:mechanical-keyboard p4:bluetooth-speaker p5:usb-hub
 p6:tshirt p7:hoodie p8:jeans p9:running-shoes p10:backpack
 p11:desk-lamp p12:coffee-maker p13:water-bottle p14:desk-organizer p15:led-light
 p16:sunglasses p17:wallet p18:phone-case p19:watch-strap p20:laptop-sleeve
)

# Banner
curl -sfL --max-time 15 "https://loremflickr.com/1600/400/online-shopping" -o "$DIR/banner.jpg" \
  || curl -sfL --max-time 15 "https://picsum.photos/seed/vshopbanner/1600/400" -o "$DIR/banner.jpg" \
  || echo "[!] No internet - banner skipped (fallback will show)"

# Logo — offline fallback: generates a tiny valid PNG (amber square) via python if download fails
if ! curl -sfL --max-time 10 "https://picsum.photos/seed/vshoplogo/80/80" -o "$DIR/logo.png"; then
  python3 - <<'EOF'
import zlib, struct
def png(w,h,rgb):
    raw=b''.join(b'\x00'+bytes(rgb)*w for _ in range(h))
    def ch(t,d): c=t+d; return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c))
    return (b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
            +ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
open("app/static/images/logo.png","wb").write(png(80,80,(254,189,105)))
EOF
  echo "[!] Logo generated locally (offline fallback)"
fi

for entry in "${products[@]}"; do
  id="${entry%%:*}"; kw="${entry##*:}"
  curl -sfL --max-time 15 "https://loremflickr.com/400/300/$kw" -o "$DIR/$id.jpg" \
    || curl -sfL --max-time 15 "https://picsum.photos/seed/$id/400/300" -o "$DIR/$id.jpg"
  [ -s "$DIR/$id.jpg" ] && echo "[+] $id.jpg" || echo "[!] $id.jpg missing - browser fallback will handle"
done
echo "[+] Images done."
