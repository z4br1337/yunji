from django.urls import path
from . import views

urlpatterns = [
    # 用户
    path('user/register', views.user_register),
    path('user/login', views.user_login),
    path('user/profile', views.user_profile),
    path('user/invite', views.use_invite_code),
    path('user/points-log', views.user_points_log),

    # 帖子
    path('post/create', views.post_create),
    path('post/list', views.post_list),
    path('post/detail', views.post_detail),

    # 评论
    path('comment/add', views.comment_add),
    path('comment/list', views.comment_list),

    # 成果（闪光时刻）
    path('achievement/create', views.achievement_create),
    path('achievement/list', views.achievement_list),

    # 成长手册
    path('growth-book/get', views.growth_book_get),
    path('growth-book/set-public', views.growth_book_set_public),

    # 私信
    path('message/send', views.message_send),
    path('message/conversations', views.message_conversations),
    path('message/history', views.message_history),

    # 图片上传
    path('upload/image', views.upload_image),

    # 管理员
    path('admin/reports', views.admin_reports),
    path('admin/post/override', views.admin_post_override),
    path('admin/post/category', views.admin_post_category),
    path('admin/post/batch-override', views.admin_post_batch_override),
    path('admin/post/real-author', views.admin_post_real_author),
    path('admin/post/pin', views.admin_post_pin),
    path('admin/post/unpin', views.admin_post_unpin),
    path('admin/user/score', views.admin_user_score),
    path('admin/user/profile', views.admin_user_profile),
    path('admin/user/list', views.admin_user_list),
    path('admin/user/posts', views.admin_user_posts),
    path('admin/user/contact', views.admin_user_contact),
    path('admin/invite/generate', views.admin_invite_generate),
    path('admin/comment/add', views.admin_comment_add),
    path('admin/achievement/pending', views.admin_achievement_pending),
    path('admin/achievement/approve', views.admin_achievement_approve),
    path('admin/achievement/reject', views.admin_achievement_reject),
    path('admin/growth-book', views.admin_growth_book),

    # 数据导出（管理员专用）
    path('admin/export-data', views.admin_export_data),
]
