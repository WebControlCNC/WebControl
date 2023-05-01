import "feather";
import "jquery";
import pako from "pako";
import * as THREE from "three";

import { OrbitControls } from "./OrbitControls.js";
import { requestPage } from "./socketEmits.js";

class Frontpage3d {
  cutSquareGroup = new THREE.Group();
  showBoard = false;
  showLabels = false;
  homeX = 0;
  homeY = 0;

  renderer = new THREE.WebGLRenderer();
  // Workarea width and height are set in initWorkarea
  w = 0;
  h = 0;

  imageShowing = 1;

  gcode = new THREE.Group();
  textLabels = new THREE.Group();
  // cutTrailGroup = new THREE.Group();

  cameraPerspective = 0; // 0 = Orthographic, 1 = Perspective
  scale = 0.07;

  cameraO = null;
  cameraP = null;

  controlsO = null;
  controlsP = null;

  view3D = true;

  blueLineMaterial = new THREE.LineBasicMaterial({ color: 0x0000ff });
  lightBlueLineMaterial = new THREE.LineBasicMaterial({ color: 0xadd8e6 });
  greenLineMaterial = new THREE.LineBasicMaterial({ color: 0x00aa00 });
  redLineMaterial = new THREE.LineBasicMaterial({ color: 0xff0000 });
  blackLineMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });
  grayLineMaterial = new THREE.LineBasicMaterial({ color: 0x777777 });

  blackDashedMaterial = new THREE.LineDashedMaterial({ color: 0x000000, dashSize: .5, gapSize: .5 });

  scene = new THREE.Scene();

  sled = new THREE.Group();
  home = new THREE.Group();
  gcodePos = new THREE.Group();
  computedSled = new THREE.Group();
  cursor = new THREE.Group();

  cursorVLine = null;
  cursorHLine = null;
  boardCutLines = null;

  boardGroup = new THREE.Group();

  boardOutlineGeometry = new THREE.BoxGeometry(96, 48, 0.75);
  boardFillMaterial = new THREE.MeshBasicMaterial({ color: 0xD2B48C, opacity: 0.5, transparent: true })
  boardOutlineFill = new THREE.Mesh(this.boardOutlineGeometry, this.boardFillMaterial);
  boardOutlineMaterial = new THREE.LineBasicMaterial({ color: 0x783E04 })
  boardEdgesGeometry = new THREE.EdgesGeometry(this.boardOutlineGeometry)
  boardOutlineOutline = new THREE.LineSegments(this.boardEdgesGeometry, this.boardOutlineMaterial);

  isComputedEnabled = false;

  getWorkAreaSize() {
    const container = document.getElementById("workarea");
    this.w = container.clientWidth;//-20;
    this.h = container.clientHeight;//-20;
    console.log(`workarea w=${this.w}, h=${this.h}`);
    return container;
  }

  initWorkArea(renderer) {
    const container = this.getWorkAreaSize();
    renderer.setSize(this.w, this.h);

    container.appendChild(renderer.domElement);
  }

  initCamera(camera) {
    camera.position.set(0, 0, 100); //380
    camera.lookAt(0, 0, 0);
  }

  initCameraO(w, h, scale) {
    return new THREE.OrthographicCamera(w / -2 * scale, w / 2 * scale, h / 2 * scale, h / -2 * scale, 1, 100 * 500 / 380);
  }

  initCameraP(w, h) {
    return new THREE.PerspectiveCamera(45, w / h, 1, 500)
  }

  initControls(camera, renderer) {
    //setCameraPerspective(true); // true indicates initial setting
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.screenSpacePanning = true;

    return controls;
  }

  initScene(scene, blackLineMaterial, blackDashedMaterial) {
    scene.background = new THREE.Color(0xeeeeee);
    const light = new THREE.AmbientLight(0x404040); // soft white light
    scene.add(light);

    const outerFramePoints = [];
    outerFramePoints.push(new THREE.Vector3(-48, 24, 0));
    outerFramePoints.push(new THREE.Vector3(48, 24, 0));
    outerFramePoints.push(new THREE.Vector3(48, -24, 0));
    outerFramePoints.push(new THREE.Vector3(-48, -24, 0));
    outerFramePoints.push(new THREE.Vector3(-48, 24, 0));
    const outerFrameShape = new THREE.BufferGeometry().setFromPoints(outerFramePoints);
    const outerFrame = new THREE.Line(outerFrameShape, blackLineMaterial);

    const innerFramePoints = [];
    innerFramePoints.push(new THREE.Vector3(-24, 24, 0));
    innerFramePoints.push(new THREE.Vector3(-24, -24, 0));
    innerFramePoints.push(new THREE.Vector3(0, 24, 0));
    innerFramePoints.push(new THREE.Vector3(0, -24, 0));
    innerFramePoints.push(new THREE.Vector3(24, 24, 0));
    innerFramePoints.push(new THREE.Vector3(24, -24, 0));
    innerFramePoints.push(new THREE.Vector3(-48, 0, 0));
    innerFramePoints.push(new THREE.Vector3(48, 0, 0));
    const innerFrameShape = new THREE.BufferGeometry().setFromPoints(innerFramePoints);
    const innerFrame = new THREE.LineSegments(innerFrameShape, blackDashedMaterial);
    innerFrame.computeLineDistances();

    this.scene.add(outerFrame);
    this.scene.add(innerFrame);
  }

  initMarkers(marker, lineSize, circleSize, lineMaterial) {
    const sledHorizontalLinePoints = [];
    sledHorizontalLinePoints.push(new THREE.Vector3(-lineSize, 0, 0));
    sledHorizontalLinePoints.push(new THREE.Vector3(lineSize, 0, 0));
    const sledHorizontalLineSegments = new THREE.BufferGeometry().setFromPoints( sledHorizontalLinePoints );
    const sledHorizontalLine = new THREE.LineSegments(sledHorizontalLineSegments, lineMaterial);

    const sledVerticalLinePoints = [];
    sledVerticalLinePoints.push(new THREE.Vector3(0, -lineSize, 0));
    sledVerticalLinePoints.push(new THREE.Vector3(0, lineSize, 0));
    const sledVerticalLineSegments = new THREE.BufferGeometry().setFromPoints( sledVerticalLinePoints );
    const sledVerticalLine = new THREE.LineSegments(sledVerticalLineSegments, lineMaterial);

    const sledCircleGeometry = new THREE.CircleGeometry(circleSize, 32);
    const sledCircleEdges = new THREE.EdgesGeometry(sledCircleGeometry)
    const sledCircle = new THREE.LineSegments(sledCircleEdges, lineMaterial);

    marker.add(sledHorizontalLine);
    marker.add(sledVerticalLine);
    marker.add(sledCircle);
    marker.position.set(0, 0, 0);
  }

  initLineBuffers(bufferSize, drawRange, lineMaterial) {
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = new Float32Array(bufferSize * 3);
    lineGeometry.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
    lineGeometry.setDrawRange(0, drawRange);
    const line = new THREE.Line(lineGeometry, lineMaterial);
    line.frustumCulled = false;
    return line;
  }

  initBoardGroup(boardGroup, boardOutlineFill, boardOutlineOutline) {
    boardGroup.add(boardOutlineFill);
    boardGroup.add(boardOutlineOutline);

    boardGroup.position.set(0, 0, -0.75 / 2);
  }

  initAll() {
    this.initWorkArea(this.renderer);

    this.cameraO = this.initCameraO(this.w, this.h, this.scale);
    this.cameraP = this.initCameraP(this.w, this.h);
    this.initCamera(this.cameraO);
    this.initCamera(this.cameraP);
    this.controlsO = this.initControls(this.cameraO, this.renderer);
    this.controlsP = this.initControls(this.cameraP, this.renderer);
    this.toggle3DView(); // makes it not true and applies appropriate settings
    //controls.update();
    this.controlsO.saveState();
    this.controlsP.saveState();

    this.initScene(this.scene, this.blackLineMaterial, this.blackDashedMaterial);

    this.initMarkers(this.sled, 1.5, 1, this.redLineMaterial);
    this.initMarkers(this.home, 1.25, 0.75, this.greenLineMaterial);
    this.initMarkers(this.gcodePos, 1, 0.5, this.blackLineMaterial);
    this.initMarkers(this.computedSled, 1.5, 1, this.grayLineMaterial);
    this.initMarkers(this.cursor, 1.5, 1, this.blueLineMaterial);

    this.cursorVLine = this.initLineBuffers(2, 2, this.lightBlueLineMaterial);
    this.cursorHLine = this.initLineBuffers(2, 2, this.lightBlueLineMaterial);
    this.boardCutLines = this.initLineBuffers(1000, 100, this.redLineMaterial);

    this.scene.add(this.cursorVLine);
    this.scene.add(this.cursorHLine);
    this.scene.add(this.boardCutLines);

    this.initBoardGroup(this.boardGroup, this.boardOutlineFill, this.boardOutlineOutline);

    if (this.showBoard) {
      this.scene.add(this.cutSquareGroup);
      this.scene.add(this.boardGroup);
    }
    this.scene.add(this.sled);
    this.scene.add(this.home);
    this.scene.add(this.gcodePos);
    if (!window.isMobile) {
      this.scene.add(this.cursor);
    }

    //this.scene.add(this.cutSquareGroup);
  }

  toggle3DView() {
    console.log("toggling");
    if (this.view3D) {
      this.controlsO.enableRotate = false;
      this.controlsO.mouseButtons = {
        LEFT: THREE.MOUSE.RIGHT,
        MIDDLE: THREE.MOUSE.MIDDLE,
        RIGHT: THREE.MOUSE.LEFT
      };
      this.controlsP.enableRotate = false;
      this.controlsP.mouseButtons = {
        LEFT: THREE.MOUSE.RIGHT,
        MIDDLE: THREE.MOUSE.MIDDLE,
        RIGHT: THREE.MOUSE.LEFT
      }

      this.view3D = false;
      if (window.isMobile) {
        $("#mobilebutton3D").removeClass('btn-primary').addClass('btn-secondary');
      } else {
        $("#button3D").removeClass('btn-primary').addClass('btn-secondary');
      }
      console.log("toggled off");
    } else {
      this.controlsO.enableRotate = true;
      this.controlsO.mouseButtons = {
        LEFT: THREE.MOUSE.RIGHT,
        MIDDLE: THREE.MOUSE.MIDDLE,
        RIGHT: THREE.MOUSE.LEFT
      }
      this.controlsP.enableRotate = true;
      this.controlsP.mouseButtons = {
        LEFT: THREE.MOUSE.RIGHT,
        MIDDLE: THREE.MOUSE.MIDDLE,
        RIGHT: THREE.MOUSE.LEFT
      }

      this.view3D = true;
      if (window.isMobile) {
        $("#mobilebutton3D").removeClass('btn-secondary').addClass('btn-primary');
      } else {
        $("#button3D").removeClass('btn-secondary').addClass('btn-primary');
      }
      console.log("toggled on");
    }
    this.controlsO.update();
    this.controlsP.update();
  }

  cursorPosition(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    const vec = new THREE.Vector3();
    const pos = new THREE.Vector3();
    vec.set(
      ((event.clientX - rect.left) / (rect.right - rect.left)) * 2 - 1,
      - ((event.clientY - rect.top) / (rect.bottom - rect.top)) * 2 + 1,
      0.5);
  
    const camera = (this.cameraPerspective == 0) ? this.cameraO : this.cameraP;
    vec.unproject(camera);
    vec.sub(camera.position).normalize();
    const distance = -camera.position.z / vec.z;
    pos.copy(camera.position).add(vec.multiplyScalar(distance));

    //console.log(pos);
    return (pos);
  }

  static animate() {
    // frontpage3d has to be initialized before coming here
    if (window.frontpage3d) {
      window.frontpage3d.controlsO.update();
      window.frontpage3d.controlsP.update();
      window.frontpage3d.renderer.render(
        window.frontpage3d.scene,
        (window.frontpage3d.cameraPerspective == 0) ? window.frontpage3d.cameraO: window.frontpage3d.cameraP
      );
    }
    window.requestAnimationFrame(Frontpage3d.animate);
  }

  static onWindowResize() {
    // frontpage3d has to be initialized before coming here
    const fp3d = window.frontpage3d;
    fp3d.getWorkAreaSize();
  
    if (fp3d.cameraO) {
      //fp3d.cameraO.aspect = window.innerWidth / window.innerHeight;
      fp3d.cameraO.left = (fp3d.w / -2) * fp3d.scale;
      fp3d.cameraO.right = (fp3d.w / 2) * fp3d.scale;
      fp3d.cameraO.top = (fp3d.h / 2) * fp3d.scale;
      fp3d.cameraO.bottom = (fp3d.h / -2) * fp3d.scale;
      fp3d.cameraO.updateProjectionMatrix();
    }

    if (fp3d.cameraP) {
      //fp3d.cameraP.aspect = window.innerWidth / window.innerHeight;
      fp3d.cameraP.aspect = fp3d.w / fp3d.h;
      fp3d.cameraP.updateProjectionMatrix();
    }
  
    if (fp3d.renderer) {
      fp3d.renderer.setSize(fp3d.w, fp3d.h);
    }
  }

  confine(value, low, high) {
    if (value < low)
      return low;
    if (value > high)
      return high;
    return value;
  }

  onMouseMove(event) {
    if (!window.isMobile) {
      this.pos = this.cursorPosition(event);
      this.cursor.position.set(this.pos.x, this.pos.y, this.pos.z);
      const linePosX = this.confine(this.pos.x, -48, 48);
      const linePosY = this.confine(this.pos.y, -24, 24);
  
      let positions = this.cursorVLine.geometry.attributes.position.array;
      positions[0] = linePosX;
      positions[1] = 24;
      positions[2] = -0.001;
      positions[3] = linePosX;
      positions[4] = -24;
      positions[5] = -0.001;
      this.cursorVLine.geometry.attributes.position.needsUpdate = true;
  
      positions = this.cursorHLine.geometry.attributes.position.array;
      positions[0] = 48;
      positions[1] = linePosY;
      positions[2] = -0.001;
      positions[3] = -48;
      positions[4] = linePosY;
      positions[5] = -0.001;
      this.cursorHLine.geometry.attributes.position.needsUpdate = true;

      if ($("#units").text() == "MM") {
        this.pos.x *= 25.4
        this.pos.y *= 25.4
      }
      $("#cursorPosition").text("X: " + this.pos.x.toFixed(2) + ", Y: " + this.pos.y.toFixed(2));
    }
  }

  board3DDataUpdate(data) {
    console.log("updating board data");
    this.boardOutlineGeometry.dispose();
    this.boardOutlineGeometry = new THREE.BoxGeometry(data.width, data.height, data.thickness);
    this.boardOutlineFill.geometry = this.boardOutlineGeometry;
    this.boardEdgesGeometry = new THREE.EdgesGeometry(this.boardOutlineGeometry)
    this.boardOutlineOutline.geometry = this.boardEdgesGeometry;
  
    this.boardOutlineFill.geometry.needsUpdate = true;
    this.boardOutlineOutline.geometry.needsUpdate = true;
    this.boardGroup.position.set(data.centerX, data.centerY, data.thickness / -2.0);
  }

  positionUpdate(x, y, z) {
    if ($("#units").text() == "MM") {
      x /= 25.4
      y /= 25.4
      z /= 25.4
    }
    this.sled.position.set(x, y, z);
    this.computedSled.position.setComponent(2, z - 0.01);
  
    //console.log("x="+x+", y="+y+", z="+z)
  }

  homePositionUpdate(x, y) {
    if ($("#units").text() == "MM") {
      x /= 25.4
      y /= 25.4
    }
    this.home.position.set(x, y, 0);
    //shift any gcode
    this.homeX = x;
    this.homeY = y;
    this.gcode.position.set(x, y, 0);
  }

  gcodePositionUpdate(x, y, z) {
    if ($("#units").text() == "MM") {
      x /= 25.4
      y /= 25.4
      z /= 25.4
    }
    this.gcodePos.position.set(x + homeX, y + homeY, z);
    //console.log("x="+x+", y="+y)
  }

  processError3d(data) {
    if (!data.computedEnabled) {
      if (this.isComputedEnabled) {
        this.scene.remove(this.computedSled);
        this.isComputedEnabled = false;
      }
      return;
    } else {
      var x = data.computedX / 25.4;
      var y = data.computedY / 25.4;
      if ($("#units").text() == "") {
        x /= 25.4
        y /= 25.4
      }
      this.computedSled.position.setComponent(0, x);
      this.computedSled.position.setComponent(1, y);
      if (!this.isComputedEnabled) {
        this.scene.add(this.computedSled);
        //this.scene.add(this.cutTrailGroup);
        this.isComputedEnabled = true;
      }
    }
  }

  ab2str(buf) {
    var bufView = new Uint16Array(buf);
    var unis = "";
    for (var i = 0; i < bufView.length; i++) {
      unis = unis + String.fromCharCode(bufView[i]);
    }
    return unis;
  }  

  gcodeUpdateCompressed(data) {
    console.log("updating gcode compressed");
    if (this.gcode.children.length != 0) {
      for (let i = this.gcode.children.length - 1; i >= 0; i--) {
        this.gcode.remove(this.gcode.children[i]);
      }
    }
    if (this.textLabels.children.length != 0) {
      for (var i = this.textLabels.children.length - 1; i >= 0; i--) {
        this.textLabels.remove(this.textLabels.children[i]);
      }
    }
  
    const greenLineDashedMaterial = new THREE.LineDashedMaterial({ color: 0x00aa00, dashSize: .1, gapSize: .1 });
  
    if ((data != null) && (data != "")) {
      var uncompressed = pako.inflate(data);
      var _str = ab2str(uncompressed);
      var data = JSON.parse(_str)
      console.log(data)

      let gcodeDashed;
      let gcodeUndashed;
      data.forEach((line) => {
        if (line.type == 'line') {
          //console.log("Line length="+line.points.length+", dashed="+line.dashed);
          if (line.dashed == true) {
            const gcodeDashedLinePoints = [];
            line.points.forEach(function (point) {
              gcodeDashedLinePoints.push(new THREE.Vector3(point[0], point[1], point[2]));
            })
            const gcodeDashedLineSegments = new THREE.BufferGeometry().setFromPoints( gcodeDashedLinePoints );
            gcodeDashed = new THREE.Line(gcodeDashedLineSegments, greenLineDashedMaterial)
            gcodeDashed.computeLineDistances();
            this.gcode.add(gcodeDashed);
          } else {
            var gcodeLinePoints = [];
            line.points.forEach(function (point) {
              gcodeLinePoints.push(new THREE.Vector3(point[0], point[1], point[2]));
            })
            var gcodeLineSegments = new THREE.BufferGeometry().setFromPoints( gcodeLinePoints );
            gcodeUndashed = new THREE.Line(gcodeLineSegments, blueLineMaterial)
            this.gcode.add(gcodeUndashed);
          }
        } else {
          if (["SpindleOnCW", "SpindleOnCCW", "SpindleOff"].includes(line.command)) {
            //(line.points[1][0]>=3) && (line.points[1][0]<=5) )
            //spindle
            var gcodeCircleGeometry = new THREE.CircleGeometry(2.25 / 32, 16);
            var gcodeCircleEdges = new THREE.EdgesGeometry(gcodeCircleGeometry)
            var circleMaterial = redLineMaterial;
            var gcodeCircle = new THREE.LineSegments(gcodeCircleEdges, circleMaterial);
            gcodeCircle.position.set(line.points[0][0], line.points[0][1], line.points[0][2]);
            this.gcode.add(gcodeCircle);
            var xFactor = 3.25;
            var yFactor = 3.25;
            if (line.command == "SpindleOff") {
              //(line.points[1][0]==5)
              xFactor = .707107 * 2.25;
              yFactor = .707107 * 2.25;
            }
  
            const gcodeLinePoints = [];
            if (line.command == "SpindleOnCCW") {
              // (line.points[1][0]==4)
              xFactor = 3.25;
              yFactor = 3.25;
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] + xFactor / 32, line.points[0][1] + yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] - xFactor / 32, line.points[0][1] + yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] + xFactor / 32, line.points[0][1] - yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] - xFactor / 32, line.points[0][1] - yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[0][2]));
            } else {
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] + xFactor / 32, line.points[0][1] + yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] + xFactor / 32, line.points[0][1] - yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] - xFactor / 32, line.points[0][1] + yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0] - xFactor / 32, line.points[0][1] - yFactor / 32, line.points[0][2]));
              gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[0][2]));
            }
            const gcodeLineSegments = new THREE.BufferGeometry().setFromPoints( gcodeLinePoints );
            gcodeUndashed = new THREE.Line(gcodeLineSegments, redLineMaterial)
            this.gcode.add(gcodeUndashed);
            if (line.command != "SpindleOff") {
              text = new SpriteText('S' + line.points[1][1].toString(), .1, 'red');
              text.position.x = line.points[0][0];
              text.position.y = line.points[0][1];
              text.position.z = line.points[0][2];
              textLabels.add(text);
            }
          } else if (line.command == "ToolChange") {
            var gcodeCircleGeometry = new THREE.CircleGeometry(2.25 / 32, 16);
            var gcodeCircleEdges = new THREE.EdgesGeometry(gcodeCircleGeometry)
            circleMaterial = redLineMaterial;
            text = new SpriteText('T' + line.points[1][1].toString(), .1, 'red');
            text.position.x = line.points[0][0];
            text.position.y = line.points[0][1];
            text.position.z = line.points[0][2];
            textLabels.add(text);
            var gcodeCircle = new THREE.LineSegments(gcodeCircleEdges, circleMaterial);
            gcodeCircle.position.set(line.points[0][0], line.points[0][1], line.points[0][2]);
            this.gcode.add(gcodeCircle);
          } else {
            var gcodeCircleGeometry = new THREE.CircleGeometry(line.points[1][0] / 32, 16);
            var gcodeCircleEdges = new THREE.EdgesGeometry(gcodeCircleGeometry)
            var circleMaterial = greenLineMaterial;
            var gcodeCircle = new THREE.LineSegments(gcodeCircleEdges, circleMaterial);
            gcodeCircle.position.set(line.points[0][0], line.points[0][1], line.points[0][2]);
            this.gcode.add(gcodeCircle);
          }
  
          const gcodeLinePoints = [];
          gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[0][2]));
          gcodeLinePoints.push(new THREE.Vector3(line.points[0][0], line.points[0][1], line.points[1][2]));
          const gcodeLineSegments = new THREE.BufferGeometry().setFromPoints( gcodeLinePoints );
          gcodeUndashed = new THREE.Line(gcodeLineSegments, blueLineMaterial)
          this.gcode.add(gcodeUndashed);
        }
      });
      this.scene.add(this.gcode);
      if (this.showLabels) {
        this.scene.add(this.textLabels);
      }
    } else {
      this.scene.remove(this.gcode);
      this.scene.remove(this.textLabels);
    }
    $("#fpCircle").hide();
  }

  toggleLabels() {
    if (this.showLabels) {
      this.scene.remove(this.textLabels);
      $("#labelsID").removeClass('btn-primary').addClass('btn-secondary');
    }
    else {
      this.scene.add(this.textLabels);
      $("#labelsID").removeClass('btn-secondary').addClass('btn-primary');
    }
    this.showLabels = !this.showLabels;
  }

  resetView() {
    this.controlsO.reset();
    this.controlsP.reset();
  }

  processCameraMessage(data) {
    if (!["cameraImageUpdated", "updateCamera"].includes(data.command)) {
      return;
    }

    if (data.command == "cameraImageUpdated") {
      var newImg = new Image();
      if (imageShowing == 1) {
        newImg.onload = function () {
          document.getElementById("cameraImage2").setAttribute('src', this.src);
          if (window.isMobile) {
            document.getElementById("mobileCameraDiv2").style.zIndex = "95";
            document.getElementById("mobileCameraDiv1").style.zIndex = "94";
          } else {
            document.getElementById("cameraDiv2").style.zIndex = "95";
            document.getElementById("cameraDiv1").style.zIndex = "94";
          }
          imageShowing = 2;
        }
      } else {
        newImg.onload = function () {
          document.getElementById("cameraImage1").setAttribute('src', this.src);
          if (window.isMobile) {
            document.getElementById("mobileCameraDiv1").style.zIndex = "95";
            document.getElementById("mobileCameraDiv2").style.zIndex = "94";
          } else {
            document.getElementById("cameraDiv1").style.zIndex = "95";
            document.getElementById("cameraDiv2").style.zIndex = "94";
          }
          imageShowing = 1;
        }
      }
      newImg.setAttribute('src', 'data:image/png;base64,' + data.data);
      return;
    }
    // data.command == "updateCamera"
    if (data.data == "on") {
      $("#videoStatus svg.feather.feather-video-off").replaceWith(feather.icons.video.toSvg());
      feather.replace();
      console.log("video on");
      document.getElementById("cameraImage1").style.display = "block";
      document.getElementById("cameraImage2").style.display = "block";
      if (window.isMobile) {
        document.getElementById("mobileCameraArea").style.display = "block";
      }
      return;
    }

    // data.data == "off"
    $("#videoStatus svg.feather.feather-video").replaceWith(feather.icons["video-off"].toSvg());
    feather.replace();
    console.log("video off");
    document.getElementById("cameraImage1").style.display = "none";
    document.getElementById("cameraImage2").style.display = "none";
    if (window.isMobile){
      document.getElementById("mobileCameraArea").style.display = "none";
    }
  }

  boardCutDataUpdateCompressed(data) {
    console.log("updating board cut data compressed");
    if (this.cutSquareGroup.children.length != 0) {
      for (var i = this.cutSquareGroup.children.length - 1; i >= 0; i--) {
        this.cutSquareGroup.remove(this.cutSquareGroup.children[i]);
      }
    }
    if (data != null) {
      //var cutSquareMaterial = new THREE.MeshBasicMaterial( {color:0xffff00, side: THREE.DoubleSide});
      var cutSquareMaterial = new THREE.MeshBasicMaterial({ color: 0xff6666 });
      // var noncutSquareMaterial = new THREE.MeshBasicMaterial({ color: 0x333333 });
      var uncompressed = pako.inflate(data);
      var _str = ab2str(uncompressed);
      var data = JSON.parse(_str)
  
      var pointsX = Math.ceil(window.board.width)
      var pointsY = Math.ceil(window.board.height)
      console.log("boardWidth=" + window.board.width)
      console.log("boardHeight=" + window.board.height)
      console.log("boardCenterY=" + window.board.centerY)
      var offsetX = pointsX / 2
      var offsetY = pointsY / 2
  
      for (var x = 0; x < pointsX; x++) {
        for (var y = 0; y < pointsY; y++) {
          if (data[x + y * pointsX]) {
            //console.log(x+", "+y);
            var geometry = new THREE.PlaneGeometry(1, 1);
            var plane = new THREE.Mesh(geometry, cutSquareMaterial);
            plane.position.set(x - offsetX + window.board.centerX, y - offsetY + window.board.centerY, 0.01);
            this.cutSquareGroup.add(plane);
          }/*
              else{
                  var geometry = new THREE.PlaneGeometry(1,1);
                  var plane = new THREE.Mesh(geometry, noncutSquareMaterial);
                  plane.position.set(x-offsetX+window.board.centerX, y-offsetY+window.board.centerY, 0.01);
                  this.cutSquareGroup.add(plane);
              }*/
        }
      }
    }
    var e = new Date();
    $("#fpCircle").hide();
  }

  toggleBoard() {
    if (this.showBoard) {
      this.showBoard = false;
      this.scene.remove(this.cutSquareGroup);
      this.scene.remove(this.boardGroup);
      $("#boardID").removeClass('btn-primary').addClass('btn-secondary');
    } else {
      this.showBoard = true;
      this.scene.add(this.cutSquareGroup);
      this.scene.add(this.boardGroup);
      $("#boardID").removeClass('btn-secondary').addClass('btn-primary');
    }
  }

  toggle3DPO() {
    this.cameraPerspective = !this.cameraPerspective;
    const txt = this.cameraPerspective == 0 ? "Ortho" : "Persp";
    const camera = this.cameraPerspective == 0 ? this.cameraO : this.cameraP;

    $("#buttonPO").text(txt);
    $("#mobilebuttonPO").text(txt);
    this.renderer.render(this.scene, camera);
  }
}

$(() => {
  // document.ready
  window.frontpage3d = new Frontpage3d();
  window.frontpage3d.initAll();
  // Note that this is a call to a static method
  window.requestAnimationFrame(Frontpage3d.animate);
  $("#workarea").contextmenu(() => {
    if (!window.frontpage3d.view3D) {
      // cursorPosition expects an event
      window.frontpage3d.pos = window.frontpage3d.cursorPosition({clientX: 0, clientY: 0});

      let x = window.frontpage3d.pos.x;
      x = x.toFixed(4);
      window.frontpage3d.pos.x = x;

      let y = window.frontpage3d.pos.y;
      y = y.toFixed(4);
      window.frontpage3d.pos.y = y;

      requestPage("screenAction", window.frontpage3d.pos);
    }
  });
  window.addEventListener("resize", Frontpage3d.onWindowResize, false);
  document.onmousemove = (event) => {
    window.frontpage3d.onMouseMove(event);
  }
});

/** You spin me right round, baby right round, like a record player, right round, round, round */
window.showFPSpinner = (msg) => {
  $("#fpCircle").show();
}
