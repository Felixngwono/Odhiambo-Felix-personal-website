from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .seo import SITEMAPS, robots_txt
from .views import (
    AdminsDashboard,
    ContactusPage,
    Portfolio,
    ResetPasswordView,
    about,
    activity_detail,
    activity_list,
    add_activity,
    add_blog,
    add_donation,
    add_event,
    add_family,
    add_faq,
    add_image,
    add_notification,
    add_picture,
    add_portfolio,
    add_project,
    add_task,
    add_testimonial,
    admin_event_view,
    already_applied,
    analytics,
    apply_for_job,
    blog,
    blog_details,
    certification_add,
    certification_delete,
    certification_detail,
    certification_list,
    certification_update,
    contact_details,
    dashboard,
    delete_activity,
    delete_blog,
    delete_donation,
    delete_event,
    delete_image,
    delete_job,
    delete_notifications,
    delete_portfolio,
    delete_profile,
    delete_project,
    delete_task,
    delete_testimonial,
    delete_volunteer,
    donate,
    donation_detail,
    donations,
    download_report,
    edit_project,
    education_journey,
    education_level,
    event_category_detail,
    event_category_list,
    event_detail,
    event_details,
    event_location_detail,
    event_location_list,
    eventsItem,
    faq_list,
    gallery_view,
    generate_full_pdf,
    index,
    job_application_list,
    job_application_success,
    job_list,
    job_posting,
    jobdetails,
    loginpage,
    logoutuser,
    mark_notification_read,
    mark_notifications_read,
    me,
    messaging,
    newsletter_subscribe,
    notifications,
    portfolio_details,
    post_job,
    project_detail,
    projects_list,
    public_contact,
    respond_to_application,
    search,
    send_event_response,
    send_response,
    sibling_detail,
    siblings_list,
    signup,
    skill_delete,
    skill_detail,
    skill_form,
    skills_view,
    subscribe_newsletter,
    support,
    support_create,
    support_delete,
    support_detail,
    support_update,
    task_details,
    tasks,
    testimonials_list,
    toggle_donation_receipt,
    toggle_task,
    update_activity,
    update_application_status,
    update_blog,
    update_donation,
    update_education,
    update_event,
    update_image,
    update_job,
    update_member,
    update_notification,
    update_portfolio,
    update_task,
    update_testimonial,
    update_user,
    update_volunteer,
    update_volunteer_status,
    user,
    user_detail,
    user_details,
    volunteer_detail,
    volunteer_list,
    volunteer_signup,
)

urlpatterns = [
    path('',me,name='me' ),
    path('robots.txt', robots_txt, name='robots'),
    path('sitemap.xml', sitemap, {'sitemaps': SITEMAPS}, name='sitemap'),
    path('index/',index,name='index' ),
    path('contact-submit/', public_contact, name='public_contact'),
    path('newsletter-subscribe/', newsletter_subscribe, name='newsletter_subscribe'),

    path('search/',search,name='search' ),

    path("signup/",signup, name="signup"),
    path("login/",loginpage, name="login"),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path("logoutuser/",logoutuser, name="logoutuser"),
    path("update_user/<int:pk>/",update_user, name="update_user"),
    path("delete_profile/<int:pk>/",delete_profile, name="delete_profile"),
    path('myuser/',user,name='myuser'),



    path('blog/', blog, name='blog'),  # URL for adding a new blog
    path('add/', add_blog, name='add_blog'),  # URL for adding a new blog
    path('update/<int:pk>/update/', update_blog, name='update_blog'),
    path('delete_blog/<int:pk>/delete/', delete_blog, name='delete_blog'),
    path('blog_details/<int:pk>', blog_details, name='blog_details'),




    path("portfolio/",Portfolio, name="portfolio"),
    path("add_portfolio/",add_portfolio, name="add_portfolio"),
    path('portfolio/<int:pk>/update/',update_portfolio, name='update_portfolio'),
    path('portfolio/delete/<int:pk>/', delete_portfolio, name='delete_portfolio'),
    path('portfolio_details/<int:pk>/', portfolio_details, name='portfolio_details'),




    path("contact_us/",ContactusPage, name="contactus"),

    path("events/",eventsItem, name='events'),
    path('add_event/', add_event, name='add_event'),
    path('categories/', event_category_list, name='event_category_list'),
    path('categories/<int:category_id>/', event_category_detail, name='event_category_detail'),
    path('locations/', event_location_list, name='event_location_list'),
    path('locations/<int:location_id>/', event_location_detail, name='event_location_detail'),
    path('event/update/<int:pk>/', update_event, name='update_event'),
    path('event/delete/<int:pk>/', delete_event, name='delete_event'),
    path('event_details/<int:pk>/', event_details, name='event_details'),



    path("about/", about, name="about"),

    path("gallery/", gallery_view, name="gallery"),
    path("add_picture/<int:sibling_id>/", add_picture, name="add_picture"),
    path('gallery/add/', add_image, name='add_image'),
    path('update_image/<int:image_id>/', update_image, name='update_image'),
    path('delete_image/<int:pk>/', delete_image, name='delete_image'),


    path("admins/", AdminsDashboard, name="admins"),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('admins/event/<int:event_id>/', admin_event_view, name='admin_event_view'),
    path('admins/event/response/<int:event_id>/', send_event_response, name='send_event_response'),
    path('contact/<int:contact_id>/', contact_details, name='contact_details'),


    path('user/<int:pk>/', user_detail, name='user_detail'),

    path('siblings/', siblings_list, name='siblings_list'),
    path('add_family/', add_family, name='add_family'),
    path('update-member/update/<int:member_id>/', update_member, name='update_member'),
    path('siblings/<int:sibling_id>/', sibling_detail, name='sibling_detail'),


    path('dashboard/', dashboard, name='dashboard'),


 # Tasks URL
    path('tasks/', tasks, name='tasks'),
    path('task_details/details/<int:pk>/', task_details, name='task_details'),
    path('add_task/', add_task, name='add_task'),
    path('update/<int:pk>/', update_task, name='update_task'),
    path('delete/<int:pk>/', delete_task, name='delete_task'),
    path('task/toggle/<int:pk>/', toggle_task, name='toggle_task'),



    # Support URL
    path('support/', support, name='support'),

    # Analytics URL
    path('analytics/', analytics, name='analytics'),

    # Notifications URL
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-all-read/', mark_notifications_read, name='mark_notifications_read'),
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
    path('add_notification/', add_notification, name='add_notification'),
    path('notifications/update/<int:pk>/', update_notification, name='update_notification'),
    path('notifications/delete/<int:pk>/', delete_notifications, name='delete_notifications'),



    # Activities URL

    path('user_details/<int:user_id>/', user_details, name='user_details'),
    path('education-journey/', education_journey, name='education_journey'),
    path('education_level/', education_level, name='education_level'),
    path('update_education/update/<int:education_id>/', update_education, name='update_education'),

    path('messaging',messaging,name='messaging' ),

    path('activities/', activity_list, name='activity_list'),
    path('activities/add/', add_activity, name='add_activity'),
    path('delete_activity/delete/<int:pk>/', delete_activity, name='delete_activity'),  # Actual deletion URL
    path('update_activity/update/<int:pk>/', update_activity, name='update_activity'),
    path('activity/<int:activity_id>/', activity_detail, name='activity_detail'),


    path('skills/', skills_view, name='skills'),
    path('certification_list', certification_list, name='certification_list'),
    path('certification_detail/<int:pk>/', certification_detail, name='certification_detail'),
    path('certification_add/', certification_add, name='certification_add'),
    path('<int:pk>/edit/', certification_update, name='certification_update'),
    path('certification_delete/<int:pk>/', certification_delete, name='certification_delete'),


    path('projects/', projects_list, name='projects_list'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    path('projects/add/', add_project, name='add_project'),
    path('projects/edit/<int:project_id>/', edit_project, name='edit_project'),
    path('projects/delete/<int:project_id>/', delete_project, name='delete_project'),

    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),

    path('download_report/', download_report, name='download_report'),

    path('fellomarley_pdf/', generate_full_pdf, name='fellomarley_pdf'),

    path('support/<int:pk>/', support_detail, name='support_detail'),
    path('support/new/', support_create, name='support_create'),
    path('support/<int:pk>/edit/', support_update, name='support_update'),
    path('support/<int:pk>/delete/', support_delete, name='support_delete'),

    path('skills/<int:pk>/', skill_detail, name='skill_detail'),
    path('skills/new/', skill_form, name='skill_create'),
    path('skills/edit/<int:pk>/', skill_form, name='skill_edit'),
    path('skills/delete/<int:pk>/', skill_delete, name='skill_delete'),



    path("send-response/<int:contact_id>/", send_response, name="send_response"),

     path('testimonials/', testimonials_list, name='testimonials_list'),
    path('testimonials/add/', add_testimonial, name='add_testimonial'),
    path('update_testimonial/<int:pk>/update/', update_testimonial, name='update_testimonial'),
    path('delete_testimonial/<int:pk>/delete/', delete_testimonial, name='delete_testimonial'),




    path('volunteers/', volunteer_list, name='volunteer_list'),
    path('volunteers/signup/', volunteer_signup, name='volunteer_signup'),
    path('volunteers/<int:pk>/', volunteer_detail, name='volunteer_detail'),
    path('volunteers/<int:pk>/edit/', update_volunteer, name='update_volunteer'),
    path('volunteers/<int:pk>/delete/', delete_volunteer, name='delete_volunteer'),
    path('volunteers/<int:pk>/status/', update_volunteer_status, name='update_volunteer_status'),

    path('jobs/', job_list, name='job_list'),
    path('jobs/posting/<int:pk>/', job_posting, name='job_posting'),
    path('jobs/applications/', job_application_list, name='job_application_list'),
    path('jobs/applications/<int:pk>/status/', update_application_status, name='update_application_status'),
    path('jobs/applications/<int:pk>/respond/', respond_to_application, name='respond_to_application'),
    path('jobdetails/<int:pk>/', jobdetails, name='jobdetails'),
    path('jobs/post/', post_job, name='post_job'),
    path('job/<int:job_id>/apply/', apply_for_job, name='apply_for_job'),
    path('job/application/success/', job_application_success, name='job_application_success'),
    path('job/<int:job_id>/already_applied/', already_applied, name='already_applied'),  # Already applied URL
    path('update_job/<int:pk>/', update_job, name='update_job'),
    path('delete_job/<int:pk>/', delete_job, name='delete_job'),



    path('donate/', donate, name='donate'),
    path('donations/', donations, name='donations'),
    path('add_donation/', add_donation, name='add_donation'),
    path('donations/<int:pk>/', donation_detail, name='donation_detail'),
    path('donations/update/<int:pk>/', update_donation, name='update_donation'),
    path('donations/delete/<int:pk>/', delete_donation, name='delete_donation'),
    path('donations/<int:pk>/receipt/', toggle_donation_receipt, name='toggle_donation_receipt'),

    path('faq/', faq_list, name='faq_list'),
    path('add_faq/', add_faq, name='add_faq'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)







