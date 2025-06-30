import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../utils/app_colors.dart';

class AppTextField extends StatefulWidget {
  final String? label;
  final String? hint;
  final String? helperText;
  final String? errorText;
  final TextEditingController? controller;
  final String? initialValue;
  final bool obscureText;
  final TextInputType keyboardType;
  final TextInputAction textInputAction;
  final List<TextInputFormatter>? inputFormatters;
  final void Function(String)? onChanged;
  final void Function(String)? onSubmitted;
  final void Function()? onTap;
  final VoidCallback? onEditingComplete;
  final String? Function(String?)? validator;
  final bool enabled;
  final bool readOnly;
  final int? maxLines;
  final int? minLines;
  final int? maxLength;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool required;
  final FocusNode? focusNode;
  final TextCapitalization textCapitalization;
  final TextAlign textAlign;
  final bool autofocus;
  final bool showCounter;
  final EdgeInsets? contentPadding;

  const AppTextField({
    super.key,
    this.label,
    this.hint,
    this.helperText,
    this.errorText,
    this.controller,
    this.initialValue,
    this.obscureText = false,
    this.keyboardType = TextInputType.text,
    this.textInputAction = TextInputAction.done,
    this.inputFormatters,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.onEditingComplete,
    this.validator,
    this.enabled = true,
    this.readOnly = false,
    this.maxLines = 1,
    this.minLines,
    this.maxLength,
    this.prefixIcon,
    this.suffixIcon,
    this.required = false,
    this.focusNode,
    this.textCapitalization = TextCapitalization.none,
    this.textAlign = TextAlign.start,
    this.autofocus = false,
    this.showCounter = false,
    this.contentPadding,
  });

  const AppTextField.email({
    super.key,
    this.label = 'Email',
    this.hint = 'Enter your email',
    this.helperText,
    this.errorText,
    this.controller,
    this.initialValue,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.onEditingComplete,
    this.validator,
    this.enabled = true,
    this.readOnly = false,
    this.required = true,
    this.focusNode,
    this.autofocus = false,
    this.contentPadding,
  })  : obscureText = false,
        keyboardType = TextInputType.emailAddress,
        textInputAction = TextInputAction.next,
        inputFormatters = null,
        maxLines = 1,
        minLines = null,
        maxLength = null,
        prefixIcon = const Icon(Icons.email_outlined),
        suffixIcon = null,
        textCapitalization = TextCapitalization.none,
        textAlign = TextAlign.start,
        showCounter = false;

  const AppTextField.password({
    super.key,
    this.label = 'Password',
    this.hint = 'Enter your password',
    this.helperText,
    this.errorText,
    this.controller,
    this.initialValue,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.onEditingComplete,
    this.validator,
    this.enabled = true,
    this.readOnly = false,
    this.required = true,
    this.focusNode,
    this.autofocus = false,
    this.contentPadding,
    this.suffixIcon,
  })  : obscureText = true,
        keyboardType = TextInputType.visiblePassword,
        textInputAction = TextInputAction.done,
        inputFormatters = null,
        maxLines = 1,
        minLines = null,
        maxLength = null,
        prefixIcon = const Icon(Icons.lock_outlined),
        textCapitalization = TextCapitalization.none,
        textAlign = TextAlign.start,
        showCounter = false;

  const AppTextField.phone({
    super.key,
    this.label = 'Phone Number',
    this.hint = 'Enter your phone number',
    this.helperText,
    this.errorText,
    this.controller,
    this.initialValue,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.onEditingComplete,
    this.validator,
    this.enabled = true,
    this.readOnly = false,
    this.required = false,
    this.focusNode,
    this.autofocus = false,
    this.contentPadding,
  })  : obscureText = false,
        keyboardType = TextInputType.phone,
        textInputAction = TextInputAction.done,
        inputFormatters = null,
        maxLines = 1,
        minLines = null,
        maxLength = null,
        prefixIcon = const Icon(Icons.phone_outlined),
        suffixIcon = null,
        textCapitalization = TextCapitalization.none,
        textAlign = TextAlign.start,
        showCounter = false;

  const AppTextField.multiline({
    super.key,
    this.label,
    this.hint,
    this.helperText,
    this.errorText,
    this.controller,
    this.initialValue,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.onEditingComplete,
    this.validator,
    this.enabled = true,
    this.readOnly = false,
    this.maxLines = 5,
    this.minLines = 3,
    this.maxLength,
    this.prefixIcon,
    this.suffixIcon,
    this.required = false,
    this.focusNode,
    this.textCapitalization = TextCapitalization.sentences,
    this.textAlign = TextAlign.start,
    this.autofocus = false,
    this.showCounter = true,
    this.contentPadding,
  })  : obscureText = false,
        keyboardType = TextInputType.multiline,
        textInputAction = TextInputAction.newline,
        inputFormatters = null;

  @override
  State<AppTextField> createState() => _AppTextFieldState();
}

class _AppTextFieldState extends State<AppTextField> {
  late bool _obscureText;

  @override
  void initState() {
    super.initState();
    _obscureText = widget.obscureText;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (widget.label != null) _buildLabel(),
        _buildTextField(),
        if (widget.helperText != null || widget.errorText != null) _buildHelperText(),
      ],
    );
  }

  Widget _buildLabel() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Text(
            widget.label!,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                  color: AppColors.gray700,
                ),
          ),
          if (widget.required)
            Text(
              ' *',
              style: TextStyle(
                color: AppColors.error,
                fontWeight: FontWeight.w500,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTextField() {
    return TextFormField(
      controller: widget.controller,
      initialValue: widget.initialValue,
      focusNode: widget.focusNode,
      obscureText: _obscureText,
      keyboardType: widget.keyboardType,
      textInputAction: widget.textInputAction,
      inputFormatters: widget.inputFormatters,
      onChanged: widget.onChanged,
      onFieldSubmitted: widget.onSubmitted,
      onTap: widget.onTap,
      onEditingComplete: widget.onEditingComplete,
      validator: widget.validator,
      enabled: widget.enabled,
      readOnly: widget.readOnly,
      maxLines: widget.maxLines,
      minLines: widget.minLines,
      maxLength: widget.maxLength,
      textCapitalization: widget.textCapitalization,
      textAlign: widget.textAlign,
      autofocus: widget.autofocus,
      decoration: InputDecoration(
        hintText: widget.hint,
        errorText: widget.errorText,
        prefixIcon: widget.prefixIcon,
        suffixIcon: _buildSuffixIcon(),
        contentPadding: widget.contentPadding ??
            const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        border: _buildBorder(),
        enabledBorder: _buildBorder(),
        focusedBorder: _buildBorder(focused: true),
        errorBorder: _buildBorder(error: true),
        focusedErrorBorder: _buildBorder(error: true, focused: true),
        disabledBorder: _buildBorder(disabled: true),
        filled: true,
        fillColor: widget.enabled ? Colors.white : AppColors.gray50,
        counterText: widget.showCounter ? null : '',
      ),
      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            color: widget.enabled ? AppColors.gray900 : AppColors.gray500,
          ),
    );
  }

  Widget? _buildSuffixIcon() {
    if (widget.obscureText) {
      return IconButton(
        icon: Icon(
          _obscureText ? Icons.visibility_outlined : Icons.visibility_off_outlined,
          color: AppColors.gray500,
        ),
        onPressed: () {
          setState(() {
            _obscureText = !_obscureText;
          });
        },
      );
    }
    return widget.suffixIcon;
  }

  Widget _buildHelperText() {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Text(
        widget.errorText ?? widget.helperText ?? '',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: widget.errorText != null ? AppColors.error : AppColors.gray600,
            ),
      ),
    );
  }

  OutlineInputBorder _buildBorder({
    bool focused = false,
    bool error = false,
    bool disabled = false,
  }) {
    Color borderColor;
    double borderWidth = 1;

    if (error) {
      borderColor = AppColors.error;
      borderWidth = 2;
    } else if (focused) {
      borderColor = AppColors.primary;
      borderWidth = 2;
    } else if (disabled) {
      borderColor = AppColors.gray300;
    } else {
      borderColor = AppColors.gray300;
    }

    return OutlineInputBorder(
      borderRadius: BorderRadius.circular(8),
      borderSide: BorderSide(
        color: borderColor,
        width: borderWidth,
      ),
    );
  }
}
