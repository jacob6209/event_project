
def number_to_farsi(n):
    farsi_numbers = {
        1: "اول",
        2: "دوم",
        3: "سوم",
        4: "چهارم",
        5: "پنجم",
        6: "ششم",
        7: "هفتم",
        8: "هشتم",
        9: "نهم",
        10: "دهم",
        11: "یازدهم",
        12: "دوازدهم",
        13: "سیزدهم",
        14: "چهاردهم",
        15: "پانزدهم",
        16: "شانزدهم",
        17: "هفدهم",
        18: "هجدهم",
        19: "نوزدهم",
        20: "بیستم",
        # Add more as needed
    }
    return farsi_numbers.get(n, str(n))

def persian_to_english_numbers(s):
    if not s:
        return s
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers = '0123456789'
    translation_table = str.maketrans(persian_numbers, english_numbers)
    return s.translate(translation_table)



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
