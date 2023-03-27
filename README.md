

# Error 1
Cuando se está en publicidad las urls de segmentos no funcionan para descargarse. Entiendo que esto ocurre con en el método `m3u8.loads`, al no poder desepaquetar las urls de los segmentos porque estas han cambiado.

Dos segmentos de un m3u8 de una playlist bien formateado se verian asi:
```text
#EXTINF:8.00800,
https://co-e4-p-e-tu1.cdn.mdstrm.com/live-stream/574463697b9817cf0886fc17/media_2000_20230327T032227_2017205.ts?aid=574462d1cab0f4d50866....
#EXTINF:8.00800,
https://co-e4-p-e-tu1.cdn.mdstrm.com/live-stream/574463697b9817cf0886fc17/media_2000_20230327T032235_2017206.ts?aid=574462d1cab0f4d5086...
```
En cambio, dos segmentos mal formateados se ve de la siguiente manera. Como verás tiene un campo extra llamado '#EXT-X-CUE-OUT-CONT:25.792/420' y esto evita que se desempaqueten bien los valores en el método `m3u8.loads`
```text
#EXTINF:8.00800,
https://co-e4-p-e-tu1.cdn.mdstrm.com/live-stream/574463697b9817cf0886fc17/media_2000_20230327T031507_2017149.ts?aid=574462d1cab0f4d5086...
#EXT-X-CUE-OUT-CONT:25.792/420
#EXTINF:8.00800,
https://co-e4-p-e-tu1.cdn.mdstrm.com/live-stream/574463697b9817cf0886fc17/media_2000_20230327T031515_2017150.ts?aid=574462d1cab0f4d5086...
#EXT-X-CUE-OUT-CONT:33.800/420
#EXTINF:8.00800,
```