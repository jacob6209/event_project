
# def calculate_priority_score(participant, event_type):
#     score = 0

#     criteria_settings = EventPrioritySetting.objects.filter(
#         event_type=event_type, is_enabled=True
#     )

#     for setting in criteria_settings:
#         criterion = setting.criterion
#         weight = setting.get_effective_weight()

#         if criterion.title == "سابقه شرکت در این نوع رویداد":
#             count = Registration.objects.filter(
#                 participant=participant,
#                 course__event__event_type=event_type
#             ).count()
#             score += count * weight

#         elif criterion.title == "سابقه استخدام":
#             years = participant.user.profile.employment_years
#             score += years * weight

#         elif criterion.title == "زوج جوان":
#             if participant.user.profile.is_young_couple:
#                 score += weight

#         elif criterion.title == "سابقه درخواست و رد شدن":
#             rejected = Registration.objects.filter(
#                 participant=participant,
#                 status="rejected",
#                 course__event__event_type=event_type
#             ).count()
#             score += rejected * weight

#     return score
