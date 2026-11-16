#!/usr/bin/env python3
"""
云迹数据备份脚本（修正版）
用法:
  set YUNJI_SERVER=https://yunji.zeabur.app
  set ADMIN_USERNAME=daoshengzsb0125
  set ADMIN_PASSWORD=你的管理员密码
  python scripts/backup_from_server.py

会登录管理员账号，调用 /api/admin/export-data 导出全量数据为 JSON，
同时下载数据中引用的所有媒体文件（头像/帖子图片/成果图片/分享文件）到本地 media 目录。
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

SERVER_URL = os.environ.get('YUNJI_SERVER', 'https://yunji.zeabur.app').rstrip('/')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'daoshengzsb0125')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
BACKUP_DIR = os.environ.get('BACKUP_DIR', r'D:\YUNJI BACKUP')
MEDIA_DIR = os.environ.get('MEDIA_DIR', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'server', 'media'))


def api_post(path, data=None, token=''):
    url = SERVER_URL + '/api' + path
    body = json.dumps(data or {}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code}: {e.read().decode("utf-8", errors="ignore")[:300]}')
        return None
    except Exception as e:
        print(f'  Error: {e}')
        return None


def collect_media_paths(obj, found):
    """递归收集 JSON 中所有包含 /media/ 的字符串。"""
    if isinstance(obj, str):
        if '/media/' in obj:
            # 提取从 /media/ 到字符串末尾（去掉查询参数）
            idx = obj.find('/media/')
            rel = obj[idx:]
            rel = rel.split('?')[0].split('#')[0]
            if rel and rel not in found:
                found.add(rel)
    elif isinstance(obj, (list, tuple)):
        for x in obj:
            collect_media_paths(x, found)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_media_paths(v, found)


def download_media(rel_path, base_url, media_dir):
    """rel_path 形如 /media/uploads/xxx.jpg"""
    rel = rel_path.lstrip('/')
    # /media/uploads/x.jpg -> uploads/x.jpg
    if rel.startswith('media/'):
        local_rel = rel[len('media/'):]
    else:
        local_rel = rel
    local_path = os.path.join(media_dir, local_rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.isfile(local_path):
        return 'skip'
    url = base_url + '/' + rel.lstrip('/')
    try:
        urllib.request.urlretrieve(url, local_path)
        return 'ok'
    except Exception as e:
        print(f'    下载失败 {url}: {e}')
        return 'fail'


def main():
    if not ADMIN_PASSWORD:
        print('错误：未设置 ADMIN_PASSWORD 环境变量。')
        print('请先设置：set ADMIN_PASSWORD=你的管理员密码  (Windows PowerShell: $env:ADMIN_PASSWORD="..." )')
        sys.exit(1)

    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)

    print('=' * 60)
    print('云迹数据备份工具（修正版）')
    print(f'服务器: {SERVER_URL}')
    print(f'备份目录: {BACKUP_DIR}')
    print(f'媒体目录: {MEDIA_DIR}')
    print('=' * 60)

    # 1. Login
    print('\n[1/4] 登录管理员账号...')
    result = api_post('/user/login', {'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD})
    if not result or result.get('code') != 0:
        print('  登录失败！请检查服务器地址、管理员账号密码。')
        print(f'  返回: {result}')
        sys.exit(1)
    token = result['data'].get('token', '')
    print(f'  登录成功: {result["data"]["user"].get("nickname")}')

    # 2. Export
    print('\n[2/4] 导出全量数据...')
    result = api_post('/admin/export-data', {}, token)
    if not result or result.get('code') != 0:
        print('  导出失败！')
        print(f'  返回: {result}')
        sys.exit(1)
    data = result['data']
    stats = {k: (len(v) if isinstance(v, list) else v) for k, v in data.items()}
    print(f'  数据统计: {json.dumps(stats, ensure_ascii=False)}')

    # 3. Save JSON
    print('\n[3/4] 保存备份文件...')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'yunji_backup_{timestamp}.json'
    filepath = os.path.join(BACKUP_DIR, filename)
    latest_path = os.path.join(BACKUP_DIR, 'latest.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(filepath) / 1024
    print(f'  已保存: {filepath} ({size_kb:.1f} KB)')
    print(f'  最新副本: {latest_path}')

    # 4. Download media
    print('\n[4/4] 下载媒体文件...')
    found = set()
    collect_media_paths(data, found)
    print(f'  发现 {len(found)} 个媒体引用')
    ok_n = skip_n = fail_n = 0
    for i, rel in enumerate(sorted(found), 1):
        status = download_media(rel, SERVER_URL, MEDIA_DIR)
        if status == 'ok':
            ok_n += 1
        elif status == 'skip':
            skip_n += 1
        else:
            fail_n += 1
        if i % 20 == 0 or i == len(found):
            print(f'  进度 {i}/{len(found)} (新下载 {ok_n}, 已存在 {skip_n}, 失败 {fail_n})')
    print(f'\n媒体下载完成：新下载 {ok_n}，已存在 {skip_n}，失败 {fail_n}')

    print(f'\n备份完成！共 {stats.get("users", 0)} 用户, '
          f'{stats.get("posts", 0)} 帖子, '
          f'{stats.get("achievements", 0)} 成果, '
          f'{stats.get("comments", 0)} 评论')


if __name__ == '__main__':
    main()
