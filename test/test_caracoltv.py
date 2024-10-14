import unittest
from caracoltv.caracoltv_utils import extract_multimedia_data
from lxml import html


class Test_CaracolTv(unittest.TestCase):
    def test_extract_multimedia_data_youtube(self):
        sample_text = """<body>
    <div class="YouTubeExternalContentUrl YouTubeVideoPlayer"><iframe class="YouTubeExternalContentUrl-iframe"
            loading="lazy" width="560" height="315" src="https://www.youtube.com/embed/4xYZWKx-jNU"
            allowfullscreen=""></iframe></div>
</body>"""
        root = html.fromstring(sample_text)
        videos = extract_multimedia_data(root)
        self.assertEqual(len(videos["youtube"]), 1)

    def test_extract_multimedia_data_mediastream(self):
        sample_text = """<body>
    <ps-mediastream class="MediaStreamVideoPlayer" data-video-player=""
        data-player-id="f1c787affec8d43e68353725818148d17" data-video-id="66f60573adadbe0e17bcdb94"
        data-video-title="Premios Desafío: Así reacciona Beba al recibir el premio a la Desafiante más dramática">
        <div class="MediaStreamVideoPlayer-media"
            data-mediastream="[{&quot;playerId&quot;:&quot;f1c787affec8d43e68353725818148d17&quot;,&quot;sourceUrl&quot;:&quot;https://mdstrm.com/embed/&quot;,&quot;videoId&quot;:&quot;66f60573adadbe0e17bcdb94&quot; }]">
            <button class="MediaStreamVideoPlayer-media-icon">
                <svg class="play-arrow">
                    <use class="play-arrow" xlink:href="#play-arrow"></use>
                </svg>
            </button>
            <picture>
                <img class="Image" alt="Beba Desafío" title="Beba Desafío"
                    srcset="https://caracoltv.brightspotcdn.com/dims4/default/1d6e794/2147483647/strip/true/crop/1280x720+0+0/resize/568x320!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F22%2F20%2F456809944c50a2db6576b89c3368%2Fshort-1.png 568w,https://caracoltv.brightspotcdn.com/dims4/default/282ac7a/2147483647/strip/true/crop/1280x720+0+0/resize/768x432!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F22%2F20%2F456809944c50a2db6576b89c3368%2Fshort-1.png 768w,https://caracoltv.brightspotcdn.com/dims4/default/5f85f6e/2147483647/strip/true/crop/1280x720+0+0/resize/1000x563!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F22%2F20%2F456809944c50a2db6576b89c3368%2Fshort-1.png 1000w"
                    width="800" height="450" loading="lazy"
                    src="https://caracoltv.brightspotcdn.com/dims4/default/834f77e/2147483647/strip/true/crop/1280x720+0+0/resize/800x450!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F22%2F20%2F456809944c50a2db6576b89c3368%2Fshort-1.png"
                    decoding="async">
            </picture>

        </div>
    </ps-mediastream>

    <ps-mediastream class="MediaStreamVideoPlayer" data-video-player=""
        data-player-id="f2bb3ab7081024c5485d3a32d7c0c67ea" data-video-id="66f6056a84241684a980482d"
        data-video-title="Beba se gana otro Premio en el Desafío: Esta fue la Pelea de la temporada">
        <div class="MediaStreamVideoPlayer-media"
            data-mediastream="[{&quot;playerId&quot;:&quot;f2bb3ab7081024c5485d3a32d7c0c67ea&quot;,&quot;sourceUrl&quot;:&quot;https://mdstrm.com/embed/&quot;,&quot;videoId&quot;:&quot;66f6056a84241684a980482d&quot; }]">
            <button class="MediaStreamVideoPlayer-media-icon">
                <svg class="play-arrow">
                    <use class="play-arrow" xlink:href="#play-arrow"></use>
                </svg>
            </button>
            <picture>
                <img class="Image" alt="Pelea de la temporada del Desafío 2024"
                    title="Pelea de la temporada del Desafío 2024"
                    srcset="https://caracoltv.brightspotcdn.com/dims4/default/081b15d/2147483647/strip/true/crop/1280x720+0+0/resize/568x320!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F55%2Fef%2F980987d242a1862fa69a107b4f09%2Fshort-2.png 568w,https://caracoltv.brightspotcdn.com/dims4/default/0430f98/2147483647/strip/true/crop/1280x720+0+0/resize/768x432!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F55%2Fef%2F980987d242a1862fa69a107b4f09%2Fshort-2.png 768w,https://caracoltv.brightspotcdn.com/dims4/default/964e4b9/2147483647/strip/true/crop/1280x720+0+0/resize/1000x563!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F55%2Fef%2F980987d242a1862fa69a107b4f09%2Fshort-2.png 1000w"
                    width="800" height="450" loading="lazy"
                    src="https://caracoltv.brightspotcdn.com/dims4/default/da426bd/2147483647/strip/true/crop/1280x720+0+0/resize/800x450!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F55%2Fef%2F980987d242a1862fa69a107b4f09%2Fshort-2.png"
                    decoding="async">
            </picture>

        </div>
    </ps-mediastream>
</body>"""
        root = html.fromstring(sample_text)
        videos = extract_multimedia_data(root)
        self.assertEqual(len(videos["mediastream"]), 2)

    def test_extract_multimedia_data_carousel(self):
        sample_text = """<body>
    <div class="Carousel-slide" style="position: absolute; left: 0%;" tabindex="-1" aria-hidden="true">
        <div class="CarouselSlide">
            <div class="CarouselSlide-media">
                <picture>
                    <img
                        src="https://caracoltv.brightspotcdn.com/dims4/default/f654159/2147483647/strip/true/crop/1300x668+0+17/resize/1440x740!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2Ff8%2F8d%2Fc2aad9a346dda5cad033ce34f127%2Fmg-2812.JPG">
                </picture>
            </div>
        </div>
    </div>
    <div class="Carousel-slide" style="position: absolute; left: 100%;" tabindex="-1" aria-hidden="true">
        <div class="CarouselSlide">
            <div class="CarouselSlide-media">
                <picture>
                    <img
                        src="https://caracoltv.brightspotcdn.com/dims4/default/0d0f5e9/2147483647/strip/true/crop/1300x668+0+0/resize/1440x740!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2F8a%2F39%2F53a07216414587d35b4cd2c67776%2Fmg-2783.JPG">
                </picture>
            </div>
        </div>
    </div>
    <div class="Carousel-slide is-selected" style="position: absolute; left: 200%;" tabindex="0">
        <div class="CarouselSlide">
            <div class="CarouselSlide-media">
                <picture>
                    <img
                        src="https://caracoltv.brightspotcdn.com/dims4/default/a36ecf4/2147483647/strip/true/crop/1300x668+0+0/resize/1440x740!/quality/90/?url=http%3A%2F%2Fcaracol-brightspot.s3.us-west-2.amazonaws.com%2Fa9%2F84%2F0afd90674383ae3201343da24da8%2Fmg-2882.JPG">
                </picture>
            </div>
        </div>
    </div>
</body>"""
        root = html.fromstring(sample_text)
        videos = extract_multimedia_data(root)
        self.assertEqual(len(videos["carousel"]), 3)


if __name__ == "__main__":
    unittest.main()
