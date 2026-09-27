BEGIN;

INSERT INTO sources (name, url, source_type, is_active)
VALUES
    ('vnexpress', 'https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss', 'rss', TRUE),
    ('vietnamnet', 'https://vietnamnet.vn/rss/cong-nghe.rss', 'rss', TRUE),
    ('tuoitre', 'https://tuoitre.vn/rss/cong-nghe.rss', 'rss', TRUE),
    ('nhandan', 'https://nhandan.vn/rss/khoahoc-congnghe-1292.rss', 'rss', TRUE),
    ('baotintuc', 'https://baotintuc.vn/rss/ai-1658.rss', 'rss', TRUE)
ON CONFLICT (url) DO UPDATE SET
    name = EXCLUDED.name,
    source_type = EXCLUDED.source_type,
    is_active = EXCLUDED.is_active;

COMMIT;
