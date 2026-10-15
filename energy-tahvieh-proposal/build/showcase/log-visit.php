<?php
/**
 * log-visit.php — ثبت بازدید (اختیاری، فقط روی هاست PHP)
 *
 * نصب:
 *   ۱) این فایل را کنار index.html بگذارید
 *   ۲) در index.html، درست پس از موفقیت رمزگشایی، این فراخوانی را اضافه کنید:
 *        fetch('log-visit.php', {method:'POST', body:'ok'}).catch(function(){});
 *   ۳) در پوشه، یک فایل خالی visits.log بسازید و اجازه نوشتن بدهید:
 *        chmod 660 visits.log
 *
 * چه چیزی ثبت می‌شود: زمان، IP، User-Agent، Referrer.
 * رمز سند هرگز ارسال یا ثبت نمی‌شود — رمزگشایی کاملاً سمت مرورگر است.
 *
 * چرا ارزشمند است: پس از ارسال لینک، دقیقاً می‌دانید کارفرما چند بار و چه
 * ساعت‌هایی سند را باز کرده. در پیگیری مذاکره اطلاعات عملی می‌دهد.
 */

header('Content-Type: application/json; charset=utf-8');

// فقط POST از همان دامنه
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo '{"ok":false}';
    exit;
}

$entry = [
    'time'    => date('Y-m-d H:i:s'),
    'ip'      => $_SERVER['REMOTE_ADDR']      ?? '-',
    'agent'   => substr($_SERVER['HTTP_USER_AGENT'] ?? '-', 0, 220),
    'referer' => substr($_SERVER['HTTP_REFERER']    ?? '-', 0, 220),
];

$file = __DIR__ . '/visits.log';
$line = json_encode($entry, JSON_UNESCAPED_UNICODE) . PHP_EOL;

if (@file_put_contents($file, $line, FILE_APPEND | LOCK_EX) === false) {
    http_response_code(500);
    echo '{"ok":false}';
    exit;
}

echo '{"ok":true}';
