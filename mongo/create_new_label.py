from data_schema_valid import DataValidation

def create_new_label():
    label = DataValidation(label_name, label_type) # First, we create the new label. This sets the label name and type,
                                                   # and it creates necessary attributes for the label
    if label.type == 'int':
        min_value = 0   # This is a placeholder. Needs to be defined by input.
        max_value = 0   # This is a placeholder. Needs to be defined by input.
        label.set_options(min_value=min_value, max_value=max_value)
    elif label.type == 'enum':
        enum_options = [] # This is a placeholder. Needs to be defined by input.
        label.set_options(options=enum_options)

    return label
