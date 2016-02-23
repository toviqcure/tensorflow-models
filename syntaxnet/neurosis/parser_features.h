// Sentence-based features for the transition parser.

#ifndef NLP_SAFT_COMPONENTS_DEPENDENCIES_OPENSOURCE_PARSER_FEATURES_H_
#define NLP_SAFT_COMPONENTS_DEPENDENCIES_OPENSOURCE_PARSER_FEATURES_H_

#include <string>

#include "neurosis/feature_extractor.h"
#include "neurosis/feature_types.h"
#include "neurosis/parser_state.h"
#include "task_context.h"
#include "neurosis/workspace.h"

namespace neurosis {

// A union used to represent discrete and continuous feature values.
union FloatFeatureValue {
 public:
  explicit FloatFeatureValue(FeatureValue v) : discrete_value(v) {}
  FloatFeatureValue(uint32 i, float w) : id(i), weight(w) {}
  FeatureValue discrete_value;
  struct {
    uint32 id;
    float weight;
  };
};

typedef FeatureFunction<ParserState> ParserFeatureFunction;

// Feature function for the transition parser based on a parser state object and
// a token index. This typically extracts information from a given token.
typedef FeatureFunction<ParserState, int> ParserIndexFeatureFunction;

// Utilities to register the two types of parser features.
#define REGISTER_PARSER_FEATURE_FUNCTION(name, component) \
  REGISTER_FEATURE_FUNCTION(ParserFeatureFunction, name, component)

#define REGISTER_PARSER_IDX_FEATURE_FUNCTION(name, component) \
  REGISTER_FEATURE_FUNCTION(ParserIndexFeatureFunction, name, component)

// Alias for locator type that takes a parser state, and produces a focus
// integer that can be used on nested ParserIndexFeature objects.
template<class DER>
using ParserLocator = FeatureAddFocusLocator<DER, ParserState, int>;

// Alias for Locator type features that take (ParserState, int) signatures and
// call other ParserIndexFeatures.
template<class DER>
using ParserIndexLocator = FeatureLocator<DER, ParserState, int>;

// Feature extractor for the transition parser based on a parser state object.
typedef FeatureExtractor<ParserState> ParserFeatureExtractor;

// A simple wrapper FeatureType that adds a special "<ROOT>" type.
class RootFeatureType : public FeatureType {
 public:
  // Creates a RootFeatureType that wraps a given type and adds the special
  // "<ROOT>" value in root_value.
  RootFeatureType(const string &name, const FeatureType &wrapped_type,
                  int root_value);

  // Returns the feature value name, but with the special "<ROOT>" value.
  string GetFeatureValueName(FeatureValue value) const override;

  // Returns the original number of features plus one for the "<ROOT>" value.
  FeatureValue GetDomainSize() const override;

 private:
  // A wrapped type that handles everything else besides "<ROOT>".
  const FeatureType &wrapped_type_;

  // The reserved root value.
  int root_value_;
};

// Simple feature function that wraps a Sentence based feature
// function. It adds a "<ROOT>" feature value that is triggered whenever the
// focus is the special root token. This class is sub-classed based on the
// extracted arguments of the nested function.
template<class F>
class ParserSentenceFeatureFunction : public ParserIndexFeatureFunction {
 public:
  // Instantiates and sets up the nested feature.
  void Setup(TaskContext *context) override {
    this->feature_.set_descriptor(this->descriptor());
    this->feature_.set_prefix(this->prefix());
    this->feature_.set_extractor(this->extractor());
    feature_.Setup(context);
  }

  // Initializes the nested feature and sets feature type.
  void Init(TaskContext *context) override {
    feature_.Init(context);
    num_base_values_ = feature_.GetFeatureType()->GetDomainSize();
    set_feature_type(new RootFeatureType(
        name(), *feature_.GetFeatureType(), RootValue()));
  }

  // Passes workspace requests and preprocessing to the nested feature.
  void RequestWorkspaces(WorkspaceRegistry *registry) override {
    feature_.RequestWorkspaces(registry);
  }

  void Preprocess(WorkspaceSet *workspaces, ParserState *state) const override {
    feature_.Preprocess(workspaces, state->mutable_sentence());
  }

 protected:
  // Returns the special value to represent a root token.
  FeatureValue RootValue() const { return num_base_values_; }

  // Store the number of base values from the wrapped function so compute the
  // root value.
  int num_base_values_;

  // The wrapped feature.
  F feature_;
};

// Specialization of ParserSentenceFeatureFunction that calls the nested feature
// with (Sentence, int) arguments based on the current integer focus.
template<class F>
class BasicParserSentenceFeatureFunction :
      public ParserSentenceFeatureFunction<F> {
 public:
  FeatureValue Compute(const WorkspaceSet &workspaces, const ParserState &state,
                       int focus, const FeatureVector *result) const override {
    if (focus == -1) return this->RootValue();
    return this->feature_.Compute(workspaces, state.sentence(), focus, result);
  }
};

}  // namespace neurosis

#endif  // NLP_SAFT_COMPONENTS_DEPENDENCIES_OPENSOURCE_PARSER_FEATURES_H_
