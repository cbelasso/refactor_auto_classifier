from classifier import build_hierarchy

input_file_path = "/data-fast/data3/clyde/projects/world/documents/annotator_files/explorance_world_defs_new.xlsx"

sheet_name = "def_2"

output_file_path = "/data-fast/data3/clyde/projects/world/documents/schemas/schema_v3.json"


if __name__ == "__main__":
    hierarchy, log = build_hierarchy(
        input_file=input_file_path,
        output_file=output_file_path,
        root_name="World",
        sheet_name=sheet_name,
        indent=2,
    )
    log.print_log()
