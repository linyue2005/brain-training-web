// ============ 星空粒子效果 ============
(function () {
    let canvas, ctx;
    let stars = [];
    let animationId = null;

    function initCanvas() {
        if (canvas) return;
        canvas = document.createElement("canvas");
        canvas.id = "starfield";
        document.body.appendChild(canvas);
        ctx = canvas.getContext("2d");
        resize();
    }

    function resize() {
        if (!canvas) return;
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createStars() {
        if (!canvas) return;
        const count = Math.floor(window.innerWidth * window.innerHeight / 8000);
        stars = [];
        for (let i = 0; i < count; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1.5 + 0.3,
                alpha: Math.random() * 0.5 + 0.3,
                speedX: (Math.random() - 0.5) * 0.15,
                speedY: (Math.random() - 0.5) * 0.15,
                twinkleSpeed: Math.random() * 0.02 + 0.005
            });
        }
    }

    function draw() {
        if (!ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(s => {
            s.alpha += s.twinkleSpeed;
            if (s.alpha > 0.9 || s.alpha < 0.2) s.twinkleSpeed = -s.twinkleSpeed;
            s.x += s.speedX;
            s.y += s.speedY;
            if (s.x < 0) s.x = canvas.width;
            if (s.x > canvas.width) s.x = 0;
            if (s.y < 0) s.y = canvas.height;
            if (s.y > canvas.height) s.y = 0;

            ctx.beginPath();
            ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${s.alpha})`;
            ctx.fill();
        });
        animationId = requestAnimationFrame(draw);
    }

    function start() {
        initCanvas();
        resize();
        createStars();
        if (animationId) cancelAnimationFrame(animationId);
        draw();
    }

    function stop() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
        if (ctx && canvas) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    // 窗口大小变化
    window.addEventListener("resize", () => {
        if (document.body.classList.contains("dark")) {
            resize();
            createStars();
        }
    });

    // 对外暴露
    window.updateStarfield = function () {
        if (document.body.classList.contains("dark")) {
            start();
        } else {
            stop();
        }
    };
})();