from lingua_franca.parse import annotate_datetime, annotate_duration

# reverse of extract,
# annotate returns extracted_thing, text_containing_it  vs extracted_thing, text_remainder
print(annotate_datetime("tomorrow is my birthday"))
print(annotate_duration("it took me 3 hours to finish"))
