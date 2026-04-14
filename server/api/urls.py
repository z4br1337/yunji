from django.urls import path
from . import views

urlpatterns = [
    # 用户
    path('user/register', views.user_register),
    path('user/login', views.user_login),
    path('user/bind-student-id', views.bind_student_id),
    path('user/profile', views.user_profile),
    path('user/public-home', views.user_public_home),
    path('user/change-password', views.user_change_password),
    path('user/invite', views.use_invite_code),
    path('user/points-log', views.user_points_log),

    # 帖子
    path('post/create', views.post_create),
    path('post/delete', views.post_delete),
    path('post/list', views.post_list),
    path('post/detail', views.post_detail),
    path('post/like', views.post_like),
    path('topic/hot', views.topic_hot_list),
    path('post/hot-snippets', views.post_hot_snippets),
    path('campaign/current', views.campaign_current),

    # 评论
    path('comment/add', views.comment_add),
    path('comment/list', views.comment_list),
    path('comment/delete', views.comment_delete),

    # 成果（闪光时刻）
    path('achievement/create', views.achievement_create),
    path('achievement/list', views.achievement_list),

    # 成长手册
    path('growth-book/get', views.growth_book_get),
    path('growth-book/set-public', views.growth_book_set_public),

    path('wall/list', views.wall_list),
    path('wall/add', views.wall_add),
    path('wall/delete', views.wall_delete),

    # 私信
    path('message/send', views.message_send),
    path('message/conversations', views.message_conversations),
    path('message/history', views.message_history),
    path('interaction/unread-summary', views.interaction_unread_summary),
    path('interaction/mark-seen', views.interaction_mark_seen),
    path('interaction/replies-to-me', views.interaction_replies_to_me),
    path('interaction/comments-on-my-posts', views.interaction_comments_on_my_posts),

    # 图片上传
    path('upload/image', views.upload_image),
    path('upload/file', views.upload_file),

    # 文件分享
    path('file-share/create', views.file_share_create),
    path('file-share/list', views.file_share_list),
    path('file-share/like', views.file_share_like),

    # 管理员
    path('admin/reports', views.admin_reports),
    path('admin/post/override', views.admin_post_override),
    path('admin/post/category', views.admin_post_category),
    path('admin/post/batch-override', views.admin_post_batch_override),
    path('admin/post/real-author', views.admin_post_real_author),
    path('admin/post/pin', views.admin_post_pin),
    path('admin/post/unpin', views.admin_post_unpin),
    path('admin/post/featured', views.admin_post_featured),
    path('admin/user/score', views.admin_user_score),
    path('admin/user/profile', views.admin_user_profile),
    path('admin/user/list', views.admin_user_list),
    path('admin/user/posts', views.admin_user_posts),
    path('admin/user/contact', views.admin_user_contact),
    path('admin/emotion/list', views.admin_emotion_list),
    path('admin/emotion/history', views.admin_emotion_history),
    path('admin/review/history', views.admin_review_history),
    path('admin/invite/generate', views.admin_invite_generate),
    path('admin/super/promote-user', views.admin_super_promote_user),
    path('admin/comment/add', views.admin_comment_add),
    path('admin/achievement/pending', views.admin_achievement_pending),
    path('admin/achievement/approve', views.admin_achievement_approve),
    path('admin/achievement/reject', views.admin_achievement_reject),
    path('admin/growth-book', views.admin_growth_book),
    path('admin/file-share/pending', views.admin_file_share_pending),
    path('admin/file-share/list', views.admin_file_share_list),
    path('admin/file-share/approve', views.admin_file_share_approve),
    path('admin/file-share/delete', views.admin_file_share_delete),
    path('admin/campaign/save', views.admin_campaign_save),

    # 积分商店
    path('shop/items', views.shop_items),
    path('shop/exchange', views.shop_exchange),
    path('shop/my-exchanges', views.shop_my_exchanges),
    path('admin/shop/items', views.admin_shop_items),
    path('admin/shop/update-stock', views.admin_shop_update_stock),

    # 数据导出（管理员专用）
    path('admin/export-data', views.admin_export_data),
]
