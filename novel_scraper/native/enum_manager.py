from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned


class EnumManager:
    @staticmethod
    def get_or_create_enum_of_type(enum_str, enum_type):
        enum_str = enum_str.lower()
        try:
            matching_enum = enum_type.objects.get(name=enum_str)
            return matching_enum
        except ObjectDoesNotExist:
            new_enum = enum_type(name=enum_str)
            new_enum.save()
            return new_enum
        except MultipleObjectsReturned:
            raise Exception(f" [~ENUM_MANAGER] > Multiple objects of type {enum_type} and str {enum_str} exists!")