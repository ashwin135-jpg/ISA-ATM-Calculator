# streamlit_designer.py
import streamlit as st
import streamlit.components.v1 as components
import json

def run():
    st.set_page_config(layout="wide")
    st.title("ISA Designer — Live 3D Preview")

    left, right = st.columns([1, 2])

    # --- Inputs (left column) ---
    with left:
        st.header("Inputs")
        wing_area = st.number_input("Wing area S (ft²)", value=24.0, step=0.1, format="%.2f")
        wing_span = st.number_input("Wing span b (ft)", value=18.0, step=0.1, format="%.2f")
        taper = st.number_input("Taper ratio", value=0.55, step=0.01, format="%.2f")
        fuselage_length = st.number_input("Fuselage length (ft)", value=6.5, step=0.1, format="%.2f")
        fuselage_dia = st.number_input("Fuselage diameter (ft)", value=0.55, step=0.01, format="%.2f")
        clmax = st.number_input("CLmax (for notes)", value=1.6, step=0.01, format="%.2f")
        color_wing = st.color_picker("Wing color", "#2dd4bf")
        color_fuse = st.color_picker("Fuselage color", "#818cf8")
        st.markdown("---")
        st.caption("Change inputs to update the 3D preview. Use mouse to orbit and scroll to zoom.")

    # package params for the embedded HTML (convert ft to meters for visualization scale if desired)
    params = {
        "S": wing_area,
        "b": wing_span,
        "taper": taper,
        "fuselage_length": fuselage_length,
        "fuselage_dia": fuselage_dia,
        "clmax": clmax,
        "color_wing": color_wing,
        "color_fuse": color_fuse,
    }
    params_json = json.dumps(params)

    # --- Right column: 3D scene (Three.js inside HTML) ---
    with right:
        st.header("3D Preview")
        DESIGNER_HTML = f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8" />
            <style>
              html,body {{ margin:0; padding:0; height:100%; background:#070A12; }}
              #canvas-holder {{ width:100%; height:900px; display:block; }}
              .infoBox {{
                position:absolute; left:12px; top:12px; z-index:10;
                color:#dbeafe; font-family: Arial, sans-serif;
                background: rgba(2,6,23,0.45); padding:8px 10px; border-radius:8px;
                border:1px solid rgba(148,163,184,0.06);
              }}
            </style>
          </head>
          <body>
            <div class="infoBox">Drag to rotate • Scroll to zoom • Double-click to reset</div>
            <div id="canvas-holder"></div>

            <script type="module">
              // params injected by Streamlit
              const params = {params_json};

              import * as THREE from 'https://unpkg.com/three@0.152.2/build/three.module.js';
              import {{ OrbitControls }} from 'https://unpkg.com/three@0.152.2/examples/jsm/controls/OrbitControls.js';

              // sizing and scale: we will treat 1 unit = 1 ft for display convenience
              const container = document.getElementById('canvas-holder');
              const width = container.clientWidth || window.innerWidth * 0.66;
              const height = 900;

              const renderer = new THREE.WebGLRenderer({ antialias:true, alpha: true });
              renderer.setPixelRatio(window.devicePixelRatio || 1);
              renderer.setSize(width, height);
              renderer.setClearColor(0x070A12, 1);
              container.appendChild(renderer.domElement);

              const scene = new THREE.Scene();

              // camera
              const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 5000);
              camera.position.set( -params.b * 0.8, params.fuselage_length * 0.6, params.b * 0.9);
              camera.lookAt(0,0,0);

              // lights
              const hemi = new THREE.HemisphereLight(0xffffff, 0x111122, 0.6);
              scene.add(hemi);
              const dir = new THREE.DirectionalLight(0xffffff, 0.9);
              dir.position.set(50,100,30);
              scene.add(dir);

              // ground grid (subtle)
              const grid = new THREE.GridHelper(200, 40, 0x0b1220, 0x081018);
              grid.position.y = -5;
              scene.add(grid);

              // helper group
              const aircraft = new THREE.Group();
              scene.add(aircraft);

              function buildAircraft(p) {{
                // clear previous
                while (aircraft.children.length) aircraft.remove(aircraft.children[0]);

                const b = Math.max(0.01, Number(p.b)); // span in ft
                const S = Math.max(0.01, Number(p.S)); // area ft^2
                const taper = Math.max(0.01, Math.min(2, Number(p.taper)));
                const span = b;
                // estimate mean chord from area = S = span * mean_chord
                const meanChord = S / span;
                const rootChord = (2*meanChord) / (1 + taper);
                const tipChord = rootChord * taper;

                // wing: approximate as two trapezoidal plates (left & right) using BoxGeometry scaled
                const halfSpan = span / 2;
                // left wing
                const leftGeom = new THREE.BoxGeometry(halfSpan, 0.2, rootChord);
                // shift origin to root edge for nicer transform
                leftGeom.translate(-halfSpan/2, 0, 0);
                const wingMat = new THREE.MeshStandardMaterial({{ color: p.color_wing, metalness:0.2, roughness:0.5, opacity:0.98 }});
                const leftWing = new THREE.Mesh(leftGeom, wingMat);
                leftWing.rotation.x = 0;
                leftWing.position.set(-halfSpan/2, 0, 0); // small offset
                // scale Z to approximate taper (rough)
                leftWing.scale.z = rootChord;
                // rotate to give slight dihedral
                leftWing.rotation.z = Math.PI * 0.005;

                // right wing (mirror)
                const rightGeom = new THREE.BoxGeometry(halfSpan, 0.2, rootChord);
                rightGeom.translate(halfSpan/2, 0, 0);
                const rightWing = new THREE.Mesh(rightGeom, wingMat);
                rightWing.position.set(halfSpan/2, 0, 0);
                rightWing.scale.z = rootChord;
                rightWing.rotation.z = -Math.PI * 0.005;

                // Fuselage (cylinder)
                const fusel = new THREE.CylinderGeometry(p.fuselage_dia/2, p.fuselage_dia/2, p.fuselage_length, 24);
                const fusemat = new THREE.MeshStandardMaterial({{ color: p.color_fuse, metalness:0.25, roughness:0.4 }});
                const fusemesh = new THREE.Mesh(fusel, fusemat);
                fusemesh.rotation.z = Math.PI/2;
                fusemesh.position.set(0, 0, 0);

                // Simple tail - horizontal and vertical
                const tailH = new THREE.BoxGeometry(p.fuselage_length*0.25, 0.08, meanChord*0.6);
                const tailHmesh = new THREE.Mesh(tailH, wingMat);
                tailHmesh.position.set(-p.fuselage_length*0.45, 0.0, 0.0);

                const tailV = new THREE.BoxGeometry(0.08, p.fuselage_length*0.18, meanChord*0.3);
                const tailVmesh = new THREE.Mesh(tailV, wingMat);
                tailVmesh.position.set(-p.fuselage_length*0.5, 0.08, 0);

                // assemble
                aircraft.add(leftWing);
                aircraft.add(rightWing);
                aircraft.add(fusemesh);
                aircraft.add(tailHmesh);
                aircraft.add(tailVmesh);

                // bounding box helper (optional)
                const bbox = new THREE.BoxHelper(aircraft, 0x223344);
                aircraft.add(bbox);

                // center aircraft at origin
                aircraft.position.y = 0;
              }}

              // initial build
              buildAircraft(params);

              // orbit controls
              const controls = new OrbitControls(camera, renderer.domElement);
              controls.enableDamping = true;
              controls.dampingFactor = 0.07;
              controls.screenSpacePanning = false;

              const clock = new THREE.Clock();

              function animate() {{
                requestAnimationFrame(animate);
                const dt = clock.getDelta();
                controls.update();
                renderer.render(scene, camera);
              }}
              animate();

              // expose a small API for Streamlit to call by re-creating the scene when params change
              window.updateAircraft = function(newParams) {{
                // merge numeric values
                try {{
                  const p = Object.assign({{}}, params, newParams);
                  // coerce numbers
                  p.b = parseFloat(p.b);
                  p.S = parseFloat(p.S);
                  p.taper = parseFloat(p.taper);
                  p.fuselage_length = parseFloat(p.fuselage_length);
                  p.fuselage_dia = parseFloat(p.fuselage_dia);
                  // rebuild
                  buildAircraft(p);
                  // adjust camera distance for new span
                  camera.position.set(-p.b * 0.8, p.fuselage_length * 0.6, p.b * 0.9);
                }} catch (err) {{
                  console.warn("update error", err);
                }}
              }};

              // auto-resize
              window.addEventListener('resize', () => {{
                const w = container.clientWidth;
                const h = container.clientHeight || 900;
                renderer.setSize(w, h);
                camera.aspect = w/h;
                camera.updateProjectionMatrix();
              }});
            </script>
          </body>
        </html>
        """

        # embed the html; set scrolling=True to allow mobile scroll, but height fixed here
        components.html(DESIGNER_HTML, height=920, scrolling=True)

    # After rendering the component, call JS API to update if Streamlit changes (this uses a hacky JS eval)
    # Streamlit can't directly call window.updateAircraft inside the iframe, but the HTML already got params at load.
    # To force a reload with new params we can re-embed; so keep the pattern above simple.
    # (Alternative: build a custom Streamlit component for two-way comms.)

if __name__ == "__main__":
    run()
