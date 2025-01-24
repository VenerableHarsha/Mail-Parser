import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
RULES_FILE= os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'rules.json')
)
class RulesManager:
    def __init__(self, root,labels,service):
        self.root = root
        self.root.title("Rules Manager")
        self.rules = self.load_rules()
        self.labels=labels
        self.service=service

        # Main Frame
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Rules List
        self.rules_listbox = tk.Listbox(self.frame, width=60, height=15)
        self.rules_listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.refresh_rules_listbox()

        # Add Rule Button
        self.add_button = ttk.Button(self.frame, text="Add Rule", command=self.add_rule)
        self.add_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Edit Rule Button
        self.edit_button = ttk.Button(self.frame, text="Edit Rule", command=self.edit_rule)
        self.edit_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Delete Rule Button
        self.delete_button = ttk.Button(self.frame, text="Delete Rule", command=self.delete_rule)
        self.delete_button.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Apply Rules Button
        self.apply_button = ttk.Button(self.frame, text="Apply Rules", command=self.apply_rules)
        self.apply_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    def load_rules(self):
        """Load rules from the rules.json file."""
        if not os.path.exists(RULES_FILE):
            return {"rules": []}
        try:
            with open(RULES_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in rules.json.")
            return {"rules": []}


    def save_rules(self):
        """Save all rules to the rules.json file."""
        with open(RULES_FILE, "w") as file:
            json.dump(self.rules, file, indent=4)



    def refresh_rules_listbox(self):
        """Refresh the listbox with the current rules."""
        self.rules_listbox.delete(0, tk.END)
        for i, rule in enumerate(self.rules.get("rules", [])):
            description = f"Rule {i + 1}: {rule['type']} - {len(rule['conditions'])} condition(s)"
            self.rules_listbox.insert(tk.END, description)

    def add_rule(self):
        """Open a window to add a new rule."""
        RuleEditor(self, None)

    def edit_rule(self):
        """Open a window to edit the selected rule."""
        selected = self.rules_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a rule to edit.")
            return
        RuleEditor(self, selected[0])

    def delete_rule(self):
        """Delete the selected rule."""
        selected = self.rules_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a rule to delete.")
            return
        del self.rules["rules"][selected[0]]
        self.save_rules()
        self.refresh_rules_listbox()

    def apply_rules(self):
        """Trigger the process_rules function."""
        from Backend.rules import process_rules  # Import the rules processing function
        process_rules(self.service)
        messagebox.showinfo("Success", "Rules applied successfully.")


class RuleEditor:
    def __init__(self, manager, rule_index):
        self.manager = manager
        self.rule_index = rule_index
        self.root = tk.Toplevel()
        self.root.title("Edit Rule" if rule_index is not None else "Add Rule")

        # Load the rule if editing
        self.rule = (self.manager.rules["rules"][rule_index] if rule_index is not None else {"type": "Any", "conditions": [], "actions": []})

        # Rule Type Dropdown (All/Any)
        self.rule_type_label = tk.Label(self.root, text="Condition Match Type:")
        self.rule_type_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.rule_type_var = tk.StringVar(value=self.rule["type"])
        self.rule_type_dropdown = ttk.Combobox(self.root, textvariable=self.rule_type_var, state="readonly")
        self.rule_type_dropdown["values"] = ("All", "Any")
        self.rule_type_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Conditions Section
        self.conditions_frame = tk.Frame(self.root)
        self.conditions_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.conditions_label = tk.Label(self.conditions_frame, text="Conditions:")
        self.conditions_label.grid(row=0, column=0, sticky="w")

        self.add_condition_button = tk.Button(self.conditions_frame, text="Add Condition", command=self.add_condition)
        self.add_condition_button.grid(row=0, column=1, padx=5, pady=5)

        self.condition_rows = []  # To keep track of condition rows
        for condition in self.rule["conditions"]:
            self.add_condition(condition)

        # Actions Section
        self.actions_frame = tk.Frame(self.root)
        self.actions_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.actions_label = tk.Label(self.actions_frame, text="Actions:")
        self.actions_label.grid(row=0, column=0, sticky="w")


        self.mark_as_label = tk.Label(self.actions_frame, text="Mark As:")
        self.mark_as_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")


        self.mark_read_var = tk.StringVar(value="None") 
        self.mark_read_dropdown = ttk.Combobox(self.actions_frame, textvariable=self.mark_read_var, state="readonly")
        self.mark_read_dropdown["values"] = ("None", "Read", "Unread") 
        self.mark_read_dropdown.grid(row=1, column=0, sticky="w")



        self.move_to_label = tk.Label(self.actions_frame, text="Move to:")
        self.move_to_label.grid(row=2, column=0, sticky="w")

        self.move_to_var = tk.StringVar()
        for action in self.rule["actions"]:
            if action.startswith("Move to"):
                self.move_to_var.set(action.split(" ", 2)[-1])
        self.move_to_dropdown = ttk.Combobox(self.actions_frame, textvariable=self.move_to_var, state="readonly")
        self.move_to_dropdown["values"] = self.manager.labels
        self.move_to_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Save Button
        self.save_button = tk.Button(self.root, text="Save Rule", command=self.save_rule)
        self.save_button.grid(row=3, column=0, columnspan=2, pady=10)

    def add_condition(self, condition=None):
        row_index = len(self.condition_rows) + 1

        # Field Dropdown
        field_var = tk.StringVar(value=condition["field"] if condition else "")
        field_dropdown = ttk.Combobox(self.conditions_frame, textvariable=field_var, state="readonly")
        field_dropdown["values"] = ("From", "Subject", "Message", "Received Date/Time")
        field_dropdown.grid(row=row_index, column=0, padx=5, pady=2, sticky="w")

        # Predicate Dropdown
        predicate_var = tk.StringVar(value=condition["predicate"] if condition else "")
        predicate_dropdown = ttk.Combobox(self.conditions_frame, textvariable=predicate_var, state="readonly")
        predicate_dropdown["values"] = ("Contains", "Does not Contain", "Equals", "Does not Equal", "Less than", "Greater than")
        predicate_dropdown.grid(row=row_index, column=1, padx=5, pady=2, sticky="w")

        # Value Entry
        value_var = tk.StringVar(value=condition["value"] if condition else "")
        value_entry = tk.Entry(self.conditions_frame, textvariable=value_var)
        value_entry.grid(row=row_index, column=2, padx=5, pady=2, sticky="w")

        # Remove Button
        remove_button = tk.Button(self.conditions_frame, text="Remove", command=lambda: self.remove_condition(row_index - 1))
        remove_button.grid(row=row_index, column=3, padx=5, pady=2)

        # Append to condition rows
        self.condition_rows.append((field_var, predicate_var, value_var, field_dropdown, predicate_dropdown, value_entry, remove_button))

    def remove_condition(self, index):
        # Remove widgets from the grid
        for widget in self.condition_rows[index][3:]:
            widget.grid_forget()
            widget.destroy()

        # Remove the condition from the list
        del self.condition_rows[index]

        # Reorder remaining rows
        for i, row in enumerate(self.condition_rows):
            for j, widget in enumerate(row[3:]):
                widget.grid(row=i + 1, column=j, padx=5, pady=2, sticky="w")

    def save_rule(self):
            # Save the rule type
            self.rule["type"] = self.rule_type_var.get()

            # Save the conditions
            self.rule["conditions"] = []
            for row in self.condition_rows:
                field, predicate, value = row[0].get(), row[1].get(), row[2].get()
                if field and predicate and value:
                    self.rule["conditions"].append({"field": field, "predicate": predicate, "value": value})

            # Save the actions
            self.rule["actions"] = []

            # Handle "Mark as Read/Unread" action (including "None")
            if self.mark_read_var.get() == "Read":
                self.rule["actions"].append("Mark as Read")
            elif self.mark_read_var.get() == "Unread":
                self.rule["actions"].append("Mark as Unread")
            # If "None" is selected, do nothing for mark actions

            # Handle "Move to" action
            if self.move_to_var.get():
                self.rule["actions"].append(f"Move to {self.move_to_var.get()}")

            # Add or update the rule in the manager's rules
            if self.rule_index is not None:
                self.manager.rules["rules"][self.rule_index] = self.rule
            else:
                self.manager.rules["rules"].append(self.rule)

            # Save to file
            self.manager.save_rules()
            self.manager.refresh_rules_listbox()
            self.root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = RulesManager(root)
    root.mainloop()
