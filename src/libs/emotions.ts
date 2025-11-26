import { type Emotion } from "./types";


/// const size = minSize + (maxSize - minSize) * (percent / 100);
export function packCircles(
    emotions: {name:string, percent:number}[],
    width = 500,
    height = 500,
    minR = 50,
    maxR = 200,
    iterations = 300
): Emotion[] {
    if (!emotions || emotions.length === 0) return [];
    
    const centerX = width / 2;
    const centerY = height / 2;

    // sory by percent
    const sorted = [...emotions].sort((a, b) => b.percent - a.percent);

    const circles: Emotion[] = sorted.map((e, index) => {
        const r = minR + (maxR - minR) * (e.percent / 100);
        
        // the first emotion (the biggest one) is always in center
        if (index === 0) {
            return {
                ...e,
                r,
                x: centerX,
                y: centerY,
                vx: 0,
                vy: 0,
                count: undefined
            };
        }
        
        // the rest ones
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 50 + 50;
        return { 
            ...e, 
            r, 
            x: centerX + Math.cos(angle) * distance, 
            y: centerY + Math.sin(angle) * distance,
            vx: 0,
            vy: 0,
            count: undefined
        };
    });

    for (let k = 0; k < iterations; k++) {
        const centerForce = 0.01;

        for (let i = 0; i < circles.length; i++) {
            for (let j = i + 1; j < circles.length; j++) {
                const a = circles[i];
                const b = circles[j];
                const dx = b.x - a.x;
                const dy = b.y - a.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                const minDist = a.r + b.r + 2;
                
                if (dist < minDist && dist > 0) {
                    const angle = Math.atan2(dy, dx);
                    const overlap = minDist - dist;
                    const move = overlap / 2;
                    
                    if (i !== 0) {
                        a.x -= Math.cos(angle) * move;
                        a.y -= Math.sin(angle) * move;
                    } else {
                        b.x += Math.cos(angle) * move * 2;
                        b.y += Math.sin(angle) * move * 2;
                        continue;
                    }
                    
                    if (j !== 0) {
                        b.x += Math.cos(angle) * move;
                        b.y += Math.sin(angle) * move;
                    } else {
                        a.x -= Math.cos(angle) * move * 2;
                        a.y -= Math.sin(angle) * move * 2;
                    }
                }
            }
        }
        
        circles.forEach((c, index) => {
            if (index === 0) return;
            
            if (c.x - c.r < 0) c.x = c.r;
            if (c.x + c.r > width) c.x = width - c.r;
            if (c.y - c.r < 0) c.y = c.r;
            if (c.y + c.r > height) c.y = height - c.r;
        });
        
        let totalX = 0, totalY = 0;
        circles.forEach(c => {
            totalX += c.x;
            totalY += c.y;
        });
        const massX = totalX / circles.length;
        const massY = totalY / circles.length;
        
        circles.forEach((c, index) => {
            if (index === 0) return;
            
            const dx = massX - c.x;
            const dy = massY - c.y;
            c.x += dx * centerForce;
            c.y += dy * centerForce;
        });
    }

    return circles;
}