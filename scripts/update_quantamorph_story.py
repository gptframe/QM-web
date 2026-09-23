"""Apply the owner-confirmed Quantamorph production story to the static homepage."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"


def replace_section(document: str, start: str, end: str, replacement: str) -> str:
    start_at = document.index(start)
    end_at = document.index(end, start_at)
    return document[:start_at] + replacement.rstrip() + "\n\n    " + document[end_at:]


def responsive_picture(base: str, css_class: str = "") -> str:
    class_attr = f' class="{css_class}"' if css_class else ""
    return f'''<figure{class_attr} data-process-scene>
              <picture>
                <source type="image/avif" srcset="assets/{base}-960.avif 960w, assets/{base}-1536.avif 1536w" sizes="100vw">
                <source type="image/webp" srcset="assets/{base}-960.webp 960w, assets/{base}-1536.webp 1536w" sizes="100vw">
                <img src="assets/{base}-1536.webp" alt="" width="1536" height="1024" loading="lazy" decoding="async">
              </picture>
            </figure>'''


PROCESS = f'''<section class="process" id="process" aria-labelledby="process-title">
      <div class="process-intro section-shell">
        <div>
          <p class="section-index">00—10 / One continuous production route</p>
          <h2 id="process-title">Your requirement enters.<br>Your component moves forward.</h2>
        </div>
        <div class="process-intro-copy">
          <p>The journey starts before material reaches a machine. Quantamorph reviews the enquiry, defines the route and issues the quotation first.</p>
          <p>After approval, design support is added where required. Drawing-ready work can move directly into production planning.</p>
        </div>
      </div>

      <ol class="sr-only" aria-label="Quantamorph enquiry-to-supply route">
        <li>Enquiry received from a drawing, CAD file, sample or functional brief.</li>
        <li>Technical review of geometry, material, quantity and acceptance requirements.</li>
        <li>Quotation defining the proposed process, scope and assumptions.</li>
        <li>Customer approval, followed by design work where the project requires it.</li>
        <li>Raw material procurement and production planning.</li>
        <li>Stock cut to the required starting size.</li>
        <li>CNC turning, VMC milling or other selected manufacturing operations.</li>
        <li>In-process checks at the machine.</li>
        <li>Final quality inspection and release.</li>
        <li>Protective packing and order identification.</li>
        <li>Supply to the customer.</li>
      </ol>

      <div class="process-scroll" data-process-scroll>
        <div class="process-pin" data-process-pin aria-hidden="true">
          <div class="process-scenes">
            {responsive_picture("cad-requirement", "process-scene process-scene--cad is-visible")}
            {responsive_picture("cad-requirement", "process-scene process-scene--cad")}
            {responsive_picture("cad-requirement", "process-scene process-scene--cad")}
            {responsive_picture("cad-requirement", "process-scene process-scene--cad")}
            {responsive_picture("raw-material", "process-scene")}
            {responsive_picture("raw-material", "process-scene")}
            {responsive_picture("turning", "process-scene")}
            {responsive_picture("turning", "process-scene")}
            {responsive_picture("inspection", "process-scene process-scene--inspection")}
            {responsive_picture("delivery", "process-scene process-scene--delivery")}
            {responsive_picture("delivery", "process-scene process-scene--delivery")}
          </div>

          <div class="part-carrier" data-part-carrier>
            <div class="part-carrier-frame" aria-hidden="true"><i></i><i></i><span>PART / QM-001</span></div>
            <picture class="part-state is-visible" data-part-state><source type="image/avif" srcset="assets/part-cad.avif"><img src="assets/part-cad.webp" alt="" width="509" height="507" decoding="async"></picture>
            <picture class="part-state" data-part-state><source type="image/avif" srcset="assets/part-stock.avif"><img src="assets/part-stock.webp" alt="" width="510" height="507" loading="lazy" decoding="async"></picture>
            <picture class="part-state" data-part-state><source type="image/avif" srcset="assets/part-blank.avif"><img src="assets/part-blank.webp" alt="" width="509" height="507" loading="lazy" decoding="async"></picture>
            <picture class="part-state" data-part-state><source type="image/avif" srcset="assets/part-rough.avif"><img src="assets/part-rough.webp" alt="" width="509" height="513" loading="lazy" decoding="async"></picture>
            <picture class="part-state" data-part-state><source type="image/avif" srcset="assets/part-finished.avif"><img src="assets/part-finished.webp" alt="" width="510" height="513" loading="lazy" decoding="async"></picture>
            <picture class="part-state" data-part-state><source type="image/avif" srcset="assets/part-packed.avif"><img src="assets/part-packed.webp" alt="" width="509" height="513" loading="lazy" decoding="async"></picture>
            <div class="part-scan" data-part-scan></div>
            <span class="measure-line measure-line--a" data-measure-line></span>
            <span class="measure-line measure-line--b" data-measure-line></span>
          </div>

          <div class="process-shade"></div>
          <div class="process-aperture" data-process-aperture></div>
          <div class="process-grid-overlay"></div>

          <div class="process-topline">
            <span>Quantamorph / enquiry to supply</span>
            <span data-stage-readout>Stage 00 / 10</span>
          </div>

          <div class="process-captions">
            <article class="process-caption is-visible" data-process-caption><p class="caption-kicker">00 / Enquiry received</p><h3>Your enquiry<br>enters the line.</h3><p>Send a drawing, CAD file, sample or functional brief, together with quantity and target timing.</p><a href="mailto:sales@quantamorph.co.uk?subject=Manufacturing%20enquiry">Start an enquiry <span aria-hidden="true">↗</span></a></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">01 / Technical review</p><h3>Review before<br>promise.</h3><p>We assess geometry, material, quantity, interfaces, inspection needs and the questions that must be closed.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">02 / Quotation</p><h3>A clear route.<br>A clear quote.</h3><p>The quotation defines the proposed manufacturing route, commercial scope, assumptions and delivery basis.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">03 / Approval &amp; optional design</p><h3>Design where<br>the part needs it.</h3><p>After approval, Quantamorph can create or develop the design. Drawing-ready projects move directly into production planning.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">04 / Raw material</p><h3>Material enters<br>production.</h3><p>The specified grade and stock form are procured and matched to the approved requirement.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">05 / Cut to size</p><h3>The blank is<br>prepared.</h3><p>Round stock is cut to the required starting length so the machining operation begins from a controlled blank.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">06 / CNC &amp; VMC machining</p><h3>Stock becomes<br>the component.</h3><p>CNC turning establishes the rotational geometry. VMC milling and other operations are added where the drawing requires them.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">07 / In-process check</p><h3>Checked at<br>the machine.</h3><p>Key features are checked during manufacture so the process can be controlled before final inspection.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">08 / Quality inspection</p><h3>Inspect.<br>Verify. Release.</h3><p>Specified characteristics are checked against the approved drawing and the agreed inspection scope.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">09 / Packing</p><h3>Protected for<br>the journey.</h3><p>Released components are cleaned, protected, identified and packed to suit the product and delivery route.</p></article>
            <article class="process-caption" data-process-caption><p class="caption-kicker">10 / Supply</p><h3>Supplied to<br>your door.</h3><p>Quantamorph completes the route with the agreed documentation, packaging and delivery requirements.</p></article>
          </div>

          <div class="process-progress-wrap">
            <div class="process-progress-track"><i data-process-fill></i><b data-process-cursor></b></div>
            <ol class="process-progress">
              <li class="is-active" data-process-step><b>00</b><span>Enquiry</span></li><li data-process-step><b>01</b><span>Review</span></li><li data-process-step><b>02</b><span>Quote</span></li><li data-process-step><b>03</b><span>Design</span></li><li data-process-step><b>04</b><span>Material</span></li><li data-process-step><b>05</b><span>Cut</span></li><li data-process-step><b>06</b><span>Machine</span></li><li data-process-step><b>07</b><span>Check</span></li><li data-process-step><b>08</b><span>Inspect</span></li><li data-process-step><b>09</b><span>Pack</span></li><li data-process-step><b>10</b><span>Supply</span></li>
            </ol>
          </div>
        </div>

        <p class="sr-only" aria-live="polite" data-stage-live>Stage 00 of 10: Enquiry received.</p>

        <ol class="process-fallback" aria-label="Quantamorph enquiry-to-supply route">
          <li><picture><source type="image/avif" srcset="assets/part-cad.avif"><img src="assets/part-cad.webp" alt="CAD wireframe of a flanged shaft component" width="509" height="507" loading="lazy" decoding="async"></picture><div><span>00 / Enquiry</span><h3>Your enquiry enters the line.</h3><p>Send a drawing, CAD file, sample or functional brief.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-cad.avif"><img src="assets/part-cad.webp" alt="CAD wireframe under technical review" width="509" height="507" loading="lazy" decoding="async"></picture><div><span>01 / Review</span><h3>Review before promise.</h3><p>Geometry, material, quantity and acceptance needs are assessed.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-cad.avif"><img src="assets/part-cad.webp" alt="CAD component representing the quoted manufacturing route" width="509" height="507" loading="lazy" decoding="async"></picture><div><span>02 / Quotation</span><h3>A clear route. A clear quote.</h3><p>Scope, process, assumptions and delivery basis are defined.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/cad-requirement-960.avif"><img src="assets/cad-requirement-960.webp" alt="Illustrative engineering design view" width="960" height="540" loading="lazy" decoding="async"></picture><div><span>03 / Approval &amp; design</span><h3>Design where the part needs it.</h3><p>Design support is available after approval; drawing-ready work moves forward directly.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-stock.avif"><img src="assets/part-stock.webp" alt="Raw round metal stock" width="510" height="507" loading="lazy" decoding="async"></picture><div><span>04 / Material</span><h3>Material enters production.</h3><p>Grade and stock form are matched to the approved requirement.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-blank.avif"><img src="assets/part-blank.webp" alt="Round metal blank cut to size" width="509" height="507" loading="lazy" decoding="async"></picture><div><span>05 / Cut</span><h3>The blank is prepared.</h3><p>Stock is cut to the required starting size.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-rough.avif"><img src="assets/part-rough.webp" alt="Rough-turned flanged shaft component" width="509" height="513" loading="lazy" decoding="async"></picture><div><span>06 / Machine</span><h3>Stock becomes the component.</h3><p>CNC turning, VMC milling and selected operations create the geometry.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/turning-960.avif"><img src="assets/turning-960.webp" alt="CNC lathe machining operation" width="960" height="640" loading="lazy" decoding="async"></picture><div><span>07 / Machine check</span><h3>Checked at the machine.</h3><p>Key features are checked during manufacture.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/inspection-960.avif"><img src="assets/inspection-960.webp" alt="Dimensional inspection of a machined component" width="960" height="640" loading="lazy" decoding="async"></picture><div><span>08 / Inspection</span><h3>Inspect. Verify. Release.</h3><p>Specified characteristics are checked before release.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/part-packed.avif"><img src="assets/part-packed.webp" alt="Finished component protected in fitted foam" width="509" height="513" loading="lazy" decoding="async"></picture><div><span>09 / Pack</span><h3>Protected for the journey.</h3><p>Released components are protected, identified and packed.</p></div></li>
          <li><picture><source type="image/avif" srcset="assets/delivery-960.avif"><img src="assets/delivery-960.webp" alt="Protected machined component ready for supply" width="960" height="540" loading="lazy" decoding="async"></picture><div><span>10 / Supply</span><h3>Supplied to your door.</h3><p>Packaging, documentation and delivery follow the agreed order.</p></div></li>
        </ol>
      </div>
    </section>'''


CAPABILITIES = '''<section class="capabilities section-shell" id="capabilities" aria-labelledby="capabilities-title">
      <header class="section-heading section-heading--split">
        <div><p class="section-index">Capabilities / Under one Quantamorph route</p><h2 id="capabilities-title">Choose the process<br>around the requirement.</h2></div>
        <p>Quantamorph covers design, machining, toolroom, fabrication, production systems, inspection and supply. Machine envelope, material, tolerance and programme fit are confirmed against the RFQ.</p>
      </header>
      <div class="capability-switcher">
        <figure class="capability-media" id="capability-panel" role="tabpanel" aria-labelledby="capability-tab-0" tabindex="0">
          <picture data-capability-picture><source data-capability-avif type="image/avif" srcset="assets/cad-requirement-960.avif 960w, assets/cad-requirement-1536.avif 1536w" sizes="(max-width: 900px) 100vw, 58vw"><source data-capability-webp type="image/webp" srcset="assets/cad-requirement-960.webp 960w, assets/cad-requirement-1536.webp 1536w" sizes="(max-width: 900px) 100vw, 58vw"><img data-capability-image src="assets/cad-requirement-1536.webp" alt="Illustrative CAD view for product and production design" width="1536" height="865" loading="lazy" decoding="async"></picture>
          <figcaption class="capability-caption"><span data-capability-kicker>01 / Define</span><h3 data-capability-title>Design &amp; engineering</h3><p data-capability-copy>Component, tooling and production-system design developed around function, manufacture and acceptance.</p></figcaption><small>Representative process imagery</small>
        </figure>
        <div class="capability-tabs" role="tablist" aria-orientation="vertical" aria-label="Quantamorph capabilities">
          <button id="capability-tab-0" type="button" role="tab" aria-selected="true" aria-controls="capability-panel" tabindex="0" data-capability data-base="cad-requirement" data-ratio="1536 865" data-alt="Illustrative CAD view for product and production design" data-kicker="01 / Define" data-title="Design & engineering" data-copy="Component, tooling and production-system design developed around function, manufacture and acceptance."><b>01</b><span>Design &amp; engineering</span><i>Define</i></button>
          <button id="capability-tab-1" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="turning" data-ratio="1536 1024" data-alt="CNC turning operation on round stock" data-kicker="02 / Turn" data-title="CNC turning" data-copy="Round components, shafts, sleeves, flanges and rotational features produced on CNC lathes."><b>02</b><span>CNC turning</span><i>Turn</i></button>
          <button id="capability-tab-2" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="cnc-milling" data-ratio="1536 1024" data-alt="VMC milling operation on a metal component" data-kicker="03 / Mill" data-title="VMC milling" data-copy="Prismatic geometry, pockets, bores, faces and interfaces produced through vertical machining-centre operations."><b>03</b><span>VMC milling</span><i>Mill</i></button>
          <button id="capability-tab-3" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="press-tool" data-ratio="1536 1024" data-alt="Precision production tool and die components" data-kicker="04 / Toolroom" data-title="Conventional machining" data-copy="Conventional turning, milling, drilling and fitting support for toolroom work, tools, dies and one-off requirements."><b>04</b><span>Conventional toolroom</span><i>Fit</i></button>
          <button id="capability-tab-4" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="fabrication" data-ratio="1536 1024" data-alt="Controlled robotic welding operation in a fabrication cell" data-kicker="05 / Join" data-title="Fabrication" data-copy="Cutting, fabrication and welding routes for frames, guards, brackets and assembled structures."><b>05</b><span>Fabrication</span><i>Join</i></button>
          <button id="capability-tab-5" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="rough-machined" data-ratio="1536 865" data-alt="Engineered component emerging from its manufacturing stock" data-kicker="06 / Automate" data-title="Special-purpose machines" data-copy="Design and build of special-purpose machines, fixtures and production equipment around the required operation."><b>06</b><span>SPMs &amp; fixtures</span><i>Automate</i></button>
          <button id="capability-tab-6" type="button" role="tab" aria-selected="false" aria-controls="capability-panel" tabindex="-1" data-capability data-base="inspection" data-ratio="1536 1024" data-alt="Dimensional inspection of a machined component" data-kicker="07 / Release" data-title="Inspection & supply" data-copy="In-process and final inspection, protective packing, order identification and supply to the agreed scope."><b>07</b><span>Inspection &amp; supply</span><i>Release</i></button>
        </div>
      </div>
    </section>'''


SYSTEMS = '''<section class="systems" id="systems" aria-labelledby="systems-title">
      <div class="section-shell">
        <header class="section-heading section-heading--split">
          <div><p class="section-index">Quantamorph engineering / Beyond the component</p><h2 id="systems-title">Part, tool<br>or production system.</h2></div>
          <p>Quantamorph can take responsibility for the design and manufacture of the component itself, the tooling that enables it, or the special-purpose equipment around the production operation.</p>
        </header>
        <div class="systems-grid">
          <div class="systems-gallery" aria-label="Quantamorph engineering and manufacturing capability">
            <figure class="system-visual system-visual--tall reveal-item"><picture><source type="image/avif" srcset="assets/cad-requirement-960.avif"><img src="assets/cad-requirement-960.webp" alt="Illustrative CAD component design" width="960" height="540" loading="lazy" decoding="async"></picture><figcaption><span>01</span>Design engineering</figcaption></figure>
            <figure class="system-visual reveal-item"><picture><source type="image/avif" srcset="assets/turning-960.avif"><img src="assets/turning-960.webp" alt="CNC turning operation" width="960" height="640" loading="lazy" decoding="async"></picture><figcaption><span>02</span>CNC turning</figcaption></figure>
            <figure class="system-visual reveal-item"><picture><source type="image/avif" srcset="assets/fabrication-960.avif"><img src="assets/fabrication-960.webp" alt="Controlled welding operation in a fabrication cell" width="960" height="640" loading="lazy" decoding="async"></picture><figcaption><span>03</span>Fabrication</figcaption></figure>
            <figure class="system-visual reveal-item"><picture><source type="image/avif" srcset="assets/press-tool-960.avif"><img src="assets/press-tool-960.webp" alt="Precision press tool and die components" width="960" height="640" loading="lazy" decoding="async"></picture><figcaption><span>04</span>Tools &amp; dies</figcaption></figure>
          </div>
          <div class="systems-copy">
            <p class="systems-lead">The route can begin from an existing drawing, a sample or a functional requirement. Design responsibility and acceptance criteria are defined before production starts.</p>
            <ol class="systems-list">
              <li class="reveal-item"><b>01</b><div><h3>Design &amp; drawing development</h3><p>2D and 3D design for components, fixtures, tooling and production equipment, developed around function and manufacture.</p></div></li>
              <li class="reveal-item"><b>02</b><div><h3>CNC turning</h3><p>CNC lathe work for rotational components, from prepared blanks through finished features.</p></div></li>
              <li class="reveal-item"><b>03</b><div><h3>VMC milling</h3><p>Vertical machining-centre work for faces, pockets, bores and interfaces that complement turning or stand alone.</p></div></li>
              <li class="reveal-item"><b>04</b><div><h3>Conventional toolroom</h3><p>Conventional machines and fitting capability for tools, dies, repair work, development parts and one-off requirements.</p></div></li>
              <li class="reveal-item"><b>05</b><div><h3>Tools, dies &amp; fixtures</h3><p>Production tooling, workholding and checking fixtures developed around the required operation and part definition.</p></div></li>
              <li class="reveal-item"><b>06</b><div><h3>Fabrication</h3><p>Fabricated and welded structures, guards, frames, brackets and assemblies produced to the approved requirement.</p></div></li>
              <li class="reveal-item"><b>07</b><div><h3>Special-purpose machines</h3><p>SPMs and application-specific production systems designed and built around the process, interfaces and acceptance criteria.</p></div></li>
            </ol>
            <p class="systems-source"><span>Capability basis</span> These capabilities are provided by Quantamorph. Machine envelope, material, tolerance, validation, inspection and programme details are confirmed for each RFQ.</p>
          </div>
        </div>
      </div>
    </section>'''


WHY = '''<section class="why" id="why" aria-labelledby="why-title">
      <div class="why-grid section-shell">
        <div class="why-statement"><p class="section-index">Why Quantamorph / One accountable route</p><h2 id="why-title">One enquiry.<br>One engineering team.</h2></div>
        <div class="why-model reveal-item"><div class="model-node model-node--start"><span>Define</span><strong>Design &amp; quotation</strong></div><div class="model-line" aria-hidden="true"><i></i></div><div class="model-node"><span>Produce</span><strong>Manufacture &amp; inspect</strong></div><div class="model-line" aria-hidden="true"><i></i></div><div class="model-node"><span>Complete</span><strong>Pack &amp; supply</strong></div></div>
        <div class="why-copy reveal-item"><p>Quantamorph keeps design, production planning, machining, fabrication, inspection, packing and supply connected to the same approved requirement.</p><p>You have one commercial and technical point of contact from the first review to the delivered component, tool or production system.</p></div>
        <div class="why-points">
          <article class="reveal-item"><span>01</span><h3>Design when needed</h3><p>Bring a finished drawing or ask Quantamorph to develop the design after quotation approval.</p></article>
          <article class="reveal-item"><span>02</span><h3>Processes under one route</h3><p>CNC, VMC, conventional toolroom, tooling, fabrication and SPM work are coordinated against one scope.</p></article>
          <article class="reveal-item"><span>03</span><h3>Control through release</h3><p>In-process checking, final inspection, packing and supply remain tied to the agreed requirement.</p></article>
        </div>
      </div>
    </section>'''


RFQ = '''<section class="rfq section-shell" id="rfq" aria-labelledby="rfq-title">
      <header class="section-heading section-heading--split"><div><p class="section-index">RFQ / What happens next</p><h2 id="rfq-title">A clear route<br>from enquiry.</h2></div><p>Send the drawing, sample or functional brief. Quantamorph reviews it, defines the quotation and then takes the approved work through design where needed, production, inspection and supply.</p></header>
      <ol class="rfq-route">
        <li class="reveal-item"><span>01</span><h3>Enquire</h3><p>Send the requirement, quantity and target date.</p></li>
        <li class="reveal-item"><span>02</span><h3>Review</h3><p>We assess geometry, materials and acceptance needs.</p></li>
        <li class="reveal-item"><span>03</span><h3>Quote</h3><p>Route, scope, assumptions and delivery basis are defined.</p></li>
        <li class="reveal-item"><span>04</span><h3>Approve &amp; design</h3><p>Approve the order; design support is added where required.</p></li>
        <li class="reveal-item"><span>05</span><h3>Produce</h3><p>Material, cutting and selected manufacturing operations begin.</p></li>
        <li class="reveal-item"><span>06</span><h3>Inspect &amp; pack</h3><p>Checks, release and protective packing follow the agreed scope.</p></li>
        <li class="reveal-item"><span>07</span><h3>Supply</h3><p>The completed order is supplied with agreed documentation.</p></li>
      </ol>
    </section>'''


def main() -> None:
    document = INDEX.read_text(encoding="utf-8")
    document = replace_section(document, '<section class="process" id="process"', '<section class="capabilities section-shell"', PROCESS)
    document = replace_section(document, '<section class="capabilities section-shell"', '<section class="component-scope"', CAPABILITIES)
    document = replace_section(document, '<section class="systems" id="systems"', '<section class="quality"', SYSTEMS)
    document = replace_section(document, '<section class="why" id="why"', '<section class="rfq section-shell"', WHY)
    document = replace_section(document, '<section class="rfq section-shell"', '<section class="final-cta"', RFQ)
    document = document.replace('Drawing-led manufacturing coordination from requirement review to delivery.', 'Design, manufacture, inspection and supply from one accountable engineering team.')
    document = document.replace('Engineering systems', 'Engineering')
    document = document.replace('Manufacturing capability, location, inspection scope, documentation and delivery terms are confirmed for each quotation. Process imagery is illustrative unless identified otherwise.', 'Machine envelope, material, tolerance, inspection scope, documentation and delivery terms are confirmed for each quotation. Process imagery is representative.')
    INDEX.write_text(document, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
