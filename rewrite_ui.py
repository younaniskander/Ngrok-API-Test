# -*- coding: utf-8 -*-
import os
import re

src = r'c:\Users\youna\Downloads\exoskeleton_system_using_biomedical_sensor_data-main\exoskeleton_system_using_biomedical_sensor_data-main\index.html'
dst = r'c:\Users\youna\Downloads\emg+dataset+in+lower+limb\SEMG_DB1\index.html'

with open(src, 'r', encoding='utf-8') as f:
    content = f.read()

emg_bars = '''<div class="emg-channels-container">
                <div class="emg-bar-group">
                    <div class="emg-bar-label"><span>Recto Femoral (RF)</span><span id="emg-val-0">0.00</span></div>
                    <div class="emg-bar-wrapper"><div class="emg-bar-fill" id="emg-fill-0"></div></div>
                </div>
                <div class="emg-bar-group">
                    <div class="emg-bar-label"><span>Biceps Femoral (BF)</span><span id="emg-val-1">0.00</span></div>
                    <div class="emg-bar-wrapper"><div class="emg-bar-fill" id="emg-fill-1"></div></div>
                </div>
                <div class="emg-bar-group">
                    <div class="emg-bar-label"><span>Vasto Medial (VM)</span><span id="emg-val-2">0.00</span></div>
                    <div class="emg-bar-wrapper"><div class="emg-bar-fill" id="emg-fill-2"></div></div>
                </div>
                <div class="emg-bar-group">
                    <div class="emg-bar-label"><span>Semitendinoso (ST)</span><span id="emg-val-3">0.00</span></div>
                    <div class="emg-bar-wrapper"><div class="emg-bar-fill" id="emg-fill-3"></div></div>
                </div>
            </div>'''
            
content = re.sub(r'<div class=\"emg-channels-container\">.*?</section>', emg_bars + "\n        </section>", content, flags=re.DOTALL)

content = content.replace(
    '<div class="angle-value-display" id="angleDisplay">0.0°</div>',
    '<div class="angle-value-display" id="angleDisplay">0.0°</div>\n            <div class="angle-category-badge" id="categoryDisplay" style="margin-top:0.5rem; padding:0.5rem 1rem; background:rgba(16,185,129,0.2); border-radius:10px; color:#10b981; font-weight:bold;">Category: --</div>'
)

content = content.replace('const NUM_CHANNELS = 11;', 'const NUM_CHANNELS = 4;')
content = content.replace('for (let ch = 0; ch < 11; ch++)', 'for (let ch = 0; ch < 4; ch++)')
content = content.replace('for (let ch = 0; ch < 10; ch++)', 'for (let ch = 0; ch < 4; ch++)')
content = content.replace('11-channel', '4-channel')

js_update = '''updateLegVisuals(data.predicted_knee_angle);
                        document.getElementById("categoryDisplay").innerText = "Category: " + data.angle_category;'''
content = content.replace('updateLegVisuals(data.predicted_knee_angle);', js_update)

with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)
