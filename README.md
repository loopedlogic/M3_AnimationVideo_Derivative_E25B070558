# From Secant to Tangent

M3 Animation Video Project · Derivative and rate of change

The animation moves a secant across the parabola \(f(x)=x^2\) and shows how its slope converges to the tangent slope at \(x=2\). The video runs 5 minutes 9 seconds at 1920 × 1080 with English narration.

## Project files

| File | Contents |
|---|---|
| `_Video.mp4` | Narrated animation |
| `_Code/render.py` | Graph drawing, animation, voice synthesis and MP4 export |
| `_Code/scenes.py` | Six scenes, including the complete narration script |
| `_Storyboard.pdf` | Six-scene planning document with diagrams and timestamps |
| `_Viva_Notes.md` | Mathematical checks and practice questions |
| `Narration_Script.txt` | Complete spoken script, grouped by storyboard scene |

## Personalize and render

Install Python 3.10+, Pillow, FFmpeg with `flite` and `libx264`, and the DejaVu font family. On Debian or Ubuntu, FFmpeg and the fonts are available as `ffmpeg` and `fonts-dejavu-core`. Set `M3_FONT_DIR` if the fonts are installed outside `/usr/share/fonts/truetype/dejavu`.

```sh
python -m pip install Pillow
ffmpeg -hide_banner -filters
python _Code/render.py --name "M. Abhiram" --student-id "E25B070558" --output _Video.mp4
```

The opening frame uses M. Abhiram and student ID E25B070558. `_Video.mp4` is the supplied WhatsApp export (5:09, 1920 x 1080, 24 fps). The narration script is available in `Narration_Script.txt`; the current video audio uses Flite synthetic English speech. To inspect frames before generating the video, append `--preview-dir preview`. The code generates every plotted point, equation panel and narration clip locally.

## Submit

Create a public GitHub repository named `M3_AnimationVideo_Derivative_E25B070558`, with the actual student ID in the name. Upload the extracted project files together, open the public URL in a private window, and submit that URL through the instructor’s Google Form.

## Reference and credits

- Reference for the derivative definition: [OpenStax, Calculus Volume 1, §3.1, Defining the Derivative](https://openstax.org/books/calculus-volume-1/pages/3-1-defining-the-derivative).
- AI disclosure: ChatGPT assisted with scripting, storyboard, diagram design and animation code. Flite’s SLT voice synthesized the English voice-over.
- Music: none.
