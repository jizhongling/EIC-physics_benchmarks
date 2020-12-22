#ifndef UTIL_EXCEPTION
#define UTIL_EXCEPTION

#include <exception>
#include <string>

namespace eic::util {
class exception : public std::exception {
public:
  exception(std::string_view msg, std::string_view type = "exception")
      : msg_{msg}, type_{type} {}

  virtual const char* what() const throw() { return msg_.c_str(); }
  virtual const char* type() const throw() { return type_.c_str(); }
  virtual ~exception() throw() {}

private:
  std::string msg_;
  std::string type_;
};
} // namespace eic::util

#endif
