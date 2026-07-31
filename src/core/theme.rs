use image::{Rgb, RgbImage};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ThemeGroup {
    Publisher,
    Character,
    Effect,
    GameClock,
}

#[derive(Debug, Clone)]
pub struct ThemeInfo {
    pub id: i32,
    pub name: &'static str,
    pub group: ThemeGroup,
    pub primary_color: (u8, u8, u8),
    pub secondary_color: (u8, u8, u8),
}

pub fn get_theme_info(theme_id: i32) -> ThemeInfo {
    match theme_id {
        0 => ThemeInfo {
            id: 0,
            name: "Nintendo",
            group: ThemeGroup::Publisher,
            primary_color: (228, 0, 15),
            secondary_color: (255, 255, 255),
        },
        1 => ThemeInfo {
            id: 1,
            name: "Capcom",
            group: ThemeGroup::Publisher,
            primary_color: (0, 47, 167),
            secondary_color: (255, 215, 0),
        },
        2 => ThemeInfo {
            id: 2,
            name: "Taito",
            group: ThemeGroup::Publisher,
            primary_color: (0, 164, 228),
            secondary_color: (255, 255, 255),
        },
        3 => ThemeInfo {
            id: 3,
            name: "Sega",
            group: ThemeGroup::Publisher,
            primary_color: (0, 137, 207),
            secondary_color: (255, 255, 255),
        },
        4 => ThemeInfo {
            id: 4,
            name: "Cave",
            group: ThemeGroup::Publisher,
            primary_color: (139, 0, 0),
            secondary_color: (255, 140, 0),
        },
        5 => ThemeInfo {
            id: 5,
            name: "Konami",
            group: ThemeGroup::Publisher,
            primary_color: (220, 20, 60),
            secondary_color: (255, 255, 255),
        },
        6 => ThemeInfo {
            id: 6,
            name: "SNK",
            group: ThemeGroup::Publisher,
            primary_color: (0, 102, 204),
            secondary_color: (255, 255, 255),
        },
        7 => ThemeInfo {
            id: 7,
            name: "Technos",
            group: ThemeGroup::Publisher,
            primary_color: (180, 0, 0),
            secondary_color: (255, 215, 0),
        },
        8 => ThemeInfo {
            id: 8,
            name: "IGS",
            group: ThemeGroup::Publisher,
            primary_color: (0, 128, 128),
            secondary_color: (255, 255, 255),
        },
        9 => ThemeInfo {
            id: 9,
            name: "Hudson",
            group: ThemeGroup::Publisher,
            primary_color: (255, 165, 0),
            secondary_color: (0, 0, 0),
        },
        10 => ThemeInfo {
            id: 10,
            name: "Banpresto",
            group: ThemeGroup::Publisher,
            primary_color: (220, 20, 60),
            secondary_color: (255, 255, 255),
        },
        11 => ThemeInfo {
            id: 11,
            name: "Namco",
            group: ThemeGroup::Publisher,
            primary_color: (255, 0, 0),
            secondary_color: (255, 255, 0),
        },
        12 => ThemeInfo {
            id: 12,
            name: "Ryu (Animated)",
            group: ThemeGroup::Character,
            primary_color: (255, 255, 255),
            secondary_color: (200, 0, 0),
        },
        13 => ThemeInfo {
            id: 13,
            name: "Mario (Animated)",
            group: ThemeGroup::Character,
            primary_color: (228, 0, 15),
            secondary_color: (0, 0, 255),
        },
        14 => ThemeInfo {
            id: 14,
            name: "Marco (Animated)",
            group: ThemeGroup::Character,
            primary_color: (255, 215, 0),
            secondary_color: (0, 100, 0),
        },
        15 => ThemeInfo {
            id: 15,
            name: "Megaman (Animated)",
            group: ThemeGroup::Character,
            primary_color: (0, 191, 255),
            secondary_color: (0, 0, 139),
        },
        16 => ThemeInfo {
            id: 16,
            name: "Space Invader (Animated)",
            group: ThemeGroup::Character,
            primary_color: (0, 255, 0),
            secondary_color: (0, 0, 0),
        },
        17 => ThemeInfo {
            id: 17,
            name: "Bub (Animated)",
            group: ThemeGroup::Character,
            primary_color: (0, 255, 127),
            secondary_color: (255, 105, 180),
        },
        18 => ThemeInfo {
            id: 18,
            name: "Cyberpunk",
            group: ThemeGroup::Effect,
            primary_color: (0, 255, 255),
            secondary_color: (255, 0, 128),
        },
        19 => ThemeInfo {
            id: 19,
            name: "Flip Clock",
            group: ThemeGroup::Effect,
            primary_color: (240, 240, 240),
            secondary_color: (30, 30, 30),
        },
        20 => ThemeInfo {
            id: 20,
            name: "Custom Gradient",
            group: ThemeGroup::Effect,
            primary_color: (255, 255, 255),
            secondary_color: (255, 255, 255),
        },
        21 => ThemeInfo {
            id: 21,
            name: "True Matrix",
            group: ThemeGroup::Effect,
            primary_color: (0, 255, 65),
            secondary_color: (0, 50, 0),
        },
        22 => ThemeInfo {
            id: 22,
            name: "Pong Clock",
            group: ThemeGroup::GameClock,
            primary_color: (255, 255, 255),
            secondary_color: (100, 100, 100),
        },
        23 => ThemeInfo {
            id: 23,
            name: "Tetris Clock",
            group: ThemeGroup::GameClock,
            primary_color: (0, 240, 240),
            secondary_color: (240, 160, 0),
        },
        24 => ThemeInfo {
            id: 24,
            name: "Word Clock",
            group: ThemeGroup::GameClock,
            primary_color: (255, 255, 255),
            secondary_color: (80, 80, 80),
        },
        25 => ThemeInfo {
            id: 25,
            name: "Binary Clock",
            group: ThemeGroup::GameClock,
            primary_color: (0, 255, 200),
            secondary_color: (40, 40, 60),
        },
        26 => ThemeInfo {
            id: 26,
            name: "Pac-Man Clock",
            group: ThemeGroup::GameClock,
            primary_color: (255, 255, 0),
            secondary_color: (255, 184, 82),
        },
        27 => ThemeInfo {
            id: 27,
            name: "Versus Health Bar",
            group: ThemeGroup::GameClock,
            primary_color: (255, 215, 0),
            secondary_color: (220, 20, 60),
        },
        28 => ThemeInfo {
            id: 28,
            name: "Slot Machine",
            group: ThemeGroup::GameClock,
            primary_color: (255, 215, 0),
            secondary_color: (138, 43, 226),
        },
        29 => ThemeInfo {
            id: 29,
            name: "Tetris Gameboy",
            group: ThemeGroup::GameClock,
            primary_color: (15, 56, 15),
            secondary_color: (139, 172, 15),
        },
        _ => ThemeInfo {
            id: -1,
            name: "Default",
            group: ThemeGroup::Publisher,
            primary_color: (255, 255, 255),
            secondary_color: (0, 0, 0),
        },
    }
}

pub fn parse_hex_color(hex: &str) -> (u8, u8, u8) {
    let s = hex.trim_start_matches('#');
    if s.len() == 6 {
        let r = u8::from_str_radix(&s[0..2], 16).unwrap_or(255);
        let g = u8::from_str_radix(&s[2..4], 16).unwrap_or(255);
        let b = u8::from_str_radix(&s[4..6], 16).unwrap_or(255);
        (r, g, b)
    } else {
        (255, 255, 255)
    }
}

pub fn interpolate_color(c1: (u8, u8, u8), c2: (u8, u8, u8), t: f32) -> (u8, u8, u8) {
    let t = t.clamp(0.0, 1.0);
    let r = (c1.0 as f32 + (c2.0 as f32 - c1.0 as f32) * t) as u8;
    let g = (c1.1 as f32 + (c2.1 as f32 - c1.1 as f32) * t) as u8;
    let b = (c1.2 as f32 + (c2.2 as f32 - c1.2 as f32) * t) as u8;
    (r, g, b)
}

pub fn generate_gradient_mask(w: u32, h: u32, c1: (u8, u8, u8), c2: (u8, u8, u8)) -> RgbImage {
    let mut img = RgbImage::new(w, h);
    for y in 0..h {
        let t = if h > 1 {
            y as f32 / (h - 1) as f32
        } else {
            0.0
        };
        let (r, g, b) = interpolate_color(c1, c2, t);
        for x in 0..w {
            img.put_pixel(x, y, Rgb([r, g, b]));
        }
    }
    img
}
